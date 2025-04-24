# Unsloth should be imported first
from math import floor
import unsloth

# Saving model
import os
from typing import Any, TypedDict, List
import warnings
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from seaborn.palettes import mpl_palette
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from trl import SFTTrainer
from transformers import TrainingArguments, TextStreamer
from unsloth.chat_templates import get_chat_template
from unsloth import FastLanguageModel
from datasets import Dataset
from unsloth import is_bfloat16_supported
import pandas as pd

from pandas import DataFrame

from tropos.preprocess_docx import StudentSubmission
from tropos.preprocess_docx.comments import CommentInfo


def filter_data(data: DataFrame) -> DataFrame:
    #
    # INPUT_LEN_FILTER = 1500
    # OUTPUT_LEN_FILTER = 4000
    #
    # # Gets the len of the context for each row
    # ln_Context = data["Context"].apply(len)
    #
    # # Filters based context len
    # filtered_data = data[ln_Context <= INPUT_LEN_FILTER]
    # # Gets the length of the response for each row
    # ln_Response = filtered_data["Response"].apply(len)
    #
    # # Filters based on response len
    # filtered_data = filtered_data[ln_Response <= OUTPUT_LEN_FILTER]
    #
    return data


os.environ["UNSLOTH_RETURN_LOGITS"] = "1"


class ProfessorFeedback(TypedDict):

    # Context
    author: str
    """
    The professors name to allow the model to personalize
    """

    requirements: str
    """ 
    The students requirements for the current paper. 
    """

    # Input
    student_paragraph: str
    """
    The student paragraph to give feedback on 
    """

    # Output
    highlighted_section: str
    """
    The section of the paragraph that the feedback applies too 
    """

    feedback: str
    """
    The feedback on the highlighted_section
    """

    rubric_response: str
    """
    The rubric result for the given paper 
    """

    essay: str
    """
    The full essay 
    """
    percent_completed: int
    """
    A value between 1-100 that dictates reading progress
    """


def process_submissions(submissions: List[StudentSubmission]) -> DataFrame:

    feedback_entries: List[ProfessorFeedback] = []
    # Process each submission
    for submission in submissions:
        rubric = submission.rubric.format_clean_and_feedback()
        requirements = submission.assignment_requirements.get_instructions()
        content = submission.submission.get_content()

        # For each comment add them to the feedback_entries
        for comment in submission.comments.results:
            comment: CommentInfo = comment
            paragraph = comment.get("paragraph")
            if 0 == len(paragraph):
                continue

            percent_chunk = content.split(paragraph)[0]
            feedback: ProfessorFeedback = {
                "highlighted_section": comment.get("commented_text"),
                "feedback": comment.get("comment_text"),
                "student_paragraph": paragraph,
                "author": comment.get("author"),
                # Not sure about having all of this here, as the mem requirements may balloon if these are included
                "requirements": requirements,
                "rubric_response": rubric,
                # This optimizes the prompt by mimicking human reading and removing the rest of the
                # essay that follows the prompt
                "essay": percent_chunk,
                "percent_completed": floor((len(percent_chunk) / len(content)) * 100),
            }
            feedback_entries.append(feedback)
        # At 100%

    return DataFrame(feedback_entries)


data_prompt = """
Your name is **{}**, and you are responsible for reviewing and providing direct, constructive feedback on student work. Your role is to assess submissions for clarity, accuracy, and completeness, while pointing out strengths and weaknesses without sugarcoating. You focus on helping students improve their understanding and performance by offering clear, actionable comments. Your feedback is detailed, objective, and tailored to the specific requirements of each assignment, with an emphasis on critical thinking, technical accuracy, and adherence to guidelines.
The `NEXT_STUDENT_PARAGRAPH` section is what is being evaluated, while giving feedback to this section make sure it makes sense to follow the previous `LAST_PARAGRAPHS` section 
Use the `EVALUATION_COMPLETION_PERCENTAGE` flag to tell if you are in the start, middle or conclusion section of an essay, when this hits 100, you must fill out a rubric. 
### LAST_PARAGRAPHS:
{}
#### EVALUATION_COMPLETION_PERCENTAGE:
{}
#### NEXT_STUDENT_PARAGRAPH:
{}
### EVALUATION:
{}"""
data_prompt_old = """Your name is {} and you are in charge of giving feedback to student work 

### Input:
#### Student Work Requirements:
    {}
#### Student Work:
    {}
### Response:
#### Highlighted Section:   
    {}
#### Feedback: 
    {}
#### Rubric:
    {} 
    """
#


class ProfessorLlama:

    # TODO: Add types
    tokenizer: Any
    model: Any
    name: str
    max_seq_length: int
    use_cached_responses: bool = False

    def __init__(
        self,
        model_name: str,
        max_seq_length: int = 4015,
        train_from_base: bool = False,
        BASE_MODEL: str = "unsloth/Llama-3.2-1B-bnb-4bit",
    ):
        """
        Allows for a base model to be set if the model name is not provided
        """
        self.model_name = model_name

        if train_from_base:
            print(f"Training a new professor based on {BASE_MODEL}")
            model_name = BASE_MODEL

        # Test to see if cutting this value in half reduces mem usage
        self.max_seq_length = max_seq_length

        # Load the model
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=model_name,
            max_seq_length=self.max_seq_length,
            load_in_4bit=True,
            dtype=None,
        )

        # A lora adapter
        self.model = FastLanguageModel.get_peft_model(
            model,
            r=16,
            lora_alpha=16,
            lora_dropout=0,
            target_modules=[
                "q_proj",
                "k_proj",
                "v_proj",
                "up_proj",
                "down_proj",
                "o_proj",
                "gate_proj",
            ],
            use_rslora=True,
            use_gradient_checkpointing="unsloth",
            random_state=37,
            loftq_config=None,
        )
        self.tokenizer = tokenizer

    def formatting_prompt(self, examples: DataFrame):
        """
        Formats the prompts based on the provided global data_prompt
        """
        authors = examples["author"]
        requirementss = examples["requirements"]
        student_paragraphs = examples["student_paragraph"]
        highlighted_sections = examples["highlighted_section"]
        feedbacks = examples["feedback"]
        rubrics = examples["rubric_response"]
        essays = examples["essay"]
        percent_progresses = examples["percent_completed"]
        texts = []

        EOS_TOKEN = self.tokenizer.eos_token
        for (
            author,
            essay,
            requirements,
            student_paragraph,
            highlighted_section,
            feedback,
            rubric,
            percent_progresses,
        ) in zip(
            authors,
            essays,
            requirementss,
            student_paragraphs,
            highlighted_sections,
            feedbacks,
            rubrics,
            percent_progresses,
        ):

            text = (
                data_prompt.format(
                    # Adding the author is similar to adding a ruler to a
                    # photo training process, it will learn the association with the author and the feedback response
                    # so there is a greater bias for a specific author
                    author,
                    essay,
                    # requirements,
                    student_paragraph,
                    percent_progresses,
                    # highlighted_section,
                    feedback,
                    # rubric,
                )
                + EOS_TOKEN
            )
            texts.append(text)

        return {
            "text": texts,
        }

    def train_llama(self, data: DataFrame):
        """
        Filters the data and trains the model with the data.
        """
        # Filter data
        filtered_data = filter_data(data)

        training_data = Dataset.from_pandas(filtered_data)
        # Maps the prompts to text
        training_data = training_data.map(self.formatting_prompt, batched=True)

        trainer = SFTTrainer(
            model=self.model,
            # tokenizer=tokenizer,
            train_dataset=training_data,
            # dataset_text_field="text",
            # max_seq_length=max_seq_length,
            # dataset_num_proc=2,
            # packing=True,
            args=TrainingArguments(
                learning_rate=3e-4,
                lr_scheduler_type="linear",
                per_device_train_batch_size=3,
                gradient_accumulation_steps=4,
                num_train_epochs=40,
                fp16=not is_bfloat16_supported(),
                bf16=is_bfloat16_supported(),
                logging_steps=1,
                optim="adamw_8bit",
                weight_decay=0.01,
                warmup_steps=10,
                output_dir="output",
                seed=37,
            ),
        )
        # Trains the model based on the information above
        trainer.train()

    def save_model(self):
        self.model.save_pretrained(self.model_name)
        self.tokenizer.save_pretrained(self.model_name)

    def get_feedback(self, author: str, paragraph: str, text: str):

        self.model = FastLanguageModel.for_inference(self.model)

        # TODO: Make sure this is consistent with the training prompt

        percent_chunk = text.split(paragraph)[0]
        percent_completed = floor((len(percent_chunk) / len(text)) * 100)

        inputs = self.tokenizer(
            [
                data_prompt.format(
                    author,
                    # student essay up until the next paragraph
                    percent_chunk,
                    # How far is left to go in the essay
                    percent_completed,
                    # The selected paragraph
                    paragraph,
                    # answer
                    "",
                )
            ],
            return_tensors="pt",
        ).to("cuda")

        outputs = self.model.generate(
            **inputs, max_new_tokens=5020, use_cache=self.use_cached_responses
        )
        answer = self.tokenizer.batch_decode(outputs)
        answer = answer[0].split("### EVALUATION:")[-1].replace("<|end_of_text|>", "")
        return answer


def call_llama(prompt: str):
    # TODO: Make this use a singleton
    pass


__all__ = ["call_llama"]
