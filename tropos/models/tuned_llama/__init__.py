# Unsloth should be imported first
import unsloth

# Saving model
import os
from math import floor
from typing import Any, TypedDict, List

from trl import SFTTrainer
from transformers import TrainingArguments
from unsloth import FastLanguageModel
from datasets import Dataset
from unsloth import is_bfloat16_supported
from pandas import DataFrame

from tropos.preprocess_docx import StudentSubmission
from tropos.preprocess_docx.comments import CommentInfo


# A required Unsloth config option
os.environ["UNSLOTH_RETURN_LOGITS"] = "1"


class ProfessorFeedbackDict(TypedDict):
    """
    The storage format used for training the model
    """

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
    """
    Processes a list of submissions into a pandas dataframe based on ProfessorFeedbackDict
    """
    feedback_entries: List[ProfessorFeedbackDict] = []
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
            feedback: ProfessorFeedbackDict = {
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


class ProfessorLlama:
    """
    A class that controls the training and prompting for feedback processing
    """

    tokenizer: Any
    """
    The tokenizer used with the model 
    """
    model: Any
    """ 
    The model that is being trained on feedback 
    """
    name: str
    """
    The path to the current model 
    """
    max_seq_length: int
    """
    Controls the length of the prompt/response 
    """
    use_cached_responses: bool = False
    """
    If the feedback from the model should be cached or not 
    """

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
        global data_prompt

        # Extract the needed columns
        authors = examples["author"]
        student_paragraphs = examples["student_paragraph"]
        feedbacks = examples["feedback"]
        essays = examples["essay"]
        percent_progresses = examples["percent_completed"]
        texts = []

        # Iterates through the dataframe and creates the prompts
        EOS_TOKEN = self.tokenizer.eos_token
        for (
            author,
            essay,
            student_paragraph,
            feedback,
            percent_progresses,
        ) in zip(
            authors,
            essays,
            student_paragraphs,
            feedbacks,
            percent_progresses,
        ):
            # NOTE: Not all of the information is used currently
            text = (
                data_prompt.format(
                    # Adding the author is similar to adding a ruler to a
                    # photo training process, it will learn the association with the author and the feedback response
                    # so there is a greater bias for a specific author
                    author,
                    essay,
                    student_paragraph,
                    percent_progresses,
                    feedback,
                )
                + EOS_TOKEN
            )
            texts.append(text)

        return {
            "text": texts,
        }

    def train_llama(self, data: DataFrame):
        """
        Trains the model with the inputted data.
        """

        # Get training data
        training_data = Dataset.from_pandas(data)

        # Maps the prompts to text
        training_data = training_data.map(self.formatting_prompt, batched=True)

        trainer = SFTTrainer(
            model=self.model,
            train_dataset=training_data,
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
        """
        Saves the model to disk
        """
        self.model.save_pretrained(self.model_name)
        self.tokenizer.save_pretrained(self.model_name)

    def get_feedback(self, author: str, paragraph: str, essay: str):
        """
        Gets feedback based on the trained model
        """
        self.model = FastLanguageModel.for_inference(self.model)

        # This splits the text up by the paragraph so the model has no context of the following paragraph
        percent_chunk = essay.split(paragraph)[0]

        # How far the model is in the current essay
        percent_completed = floor((len(percent_chunk) / len(essay)) * 100)

        # Makes the prompt and tokenizes the
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
            **inputs,
            max_new_tokens=self.max_seq_length,
            use_cache=self.use_cached_responses,
        )

        # Get the answer from the model
        answer = self.tokenizer.batch_decode(outputs)
        answer = answer[0].split("### EVALUATION:")[-1].replace("<|end_of_text|>", "")
        return answer


__all__ = []
