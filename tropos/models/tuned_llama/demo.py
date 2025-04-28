import os
from pathlib import Path
from typing import List
import gradio as gr

from tropos.markdown_printer import MarkdownFeedbackPrinter
from tropos.models.tuned_llama import ProfessorLlama, process_submissions
from tropos.preprocess_docx import StudentSubmission
from tropos.preprocess_docx.assignment_requirements import (
    AssignmentRequirements,
    parse_requirements,
)

# When more authors are added, this can change
COMMENT_AUTHOR = "Dr. H"

# This makes the markdown boxes more distinct
MARKDOWN_BOX_CSS = """
.markdown-box {
    border: 1px solid #aaa;
    padding: 12px;
    border-radius: 6px;
    background-color:  #52525b;
    display: block;
    margin: 10px 0;
}
"""

# Controls how many documents can be shown at one time
MAX_DEMO_FEEDBACK_BOXES = 10


def load_submissions(data_dir: Path) -> List[StudentSubmission]:
    """
    Loads submissions from a given directory
    """
    # Get the requirements
    reqs = parse_requirements("./" + data_dir.joinpath("Requirements.docx").__str__())

    submissions = []
    # For each folder
    for assignment_dir_part in os.listdir(data_dir):
        # Cache the dir to avoid recomputation
        assignment_dir = data_dir.joinpath(assignment_dir_part)

        if os.path.isfile(assignment_dir):
            # Skip if a file is found
            continue

        for assignment_part in os.listdir(assignment_dir):
            if assignment_part.startswith(".~"):
                # Skip temp files made by libre office
                continue

            assignment_path = assignment_dir.joinpath(assignment_part)
            submissions.append(
                StudentSubmission("./" + assignment_path.__str__(), reqs)
            )
            print(f"Loaded submission: {assignment_path}")

    return submissions


def get_all_feedback(
    model: ProfessorLlama,
    doc_path: str,
    reqs: AssignmentRequirements,
    comment_author: str,
) -> MarkdownFeedbackPrinter:
    """
    Gets all of the feedback for a given document and returns a feedback printer
    """
    printer = MarkdownFeedbackPrinter(doc_path)

    essay = StudentSubmission(doc_path, reqs).submission
    essay_content = essay.get_content()
    # NOTE: This is for easy debugging
    print("-----------------------------")
    print("Essay -------")
    print(essay_content)
    print("Feedback -------")
    for paragraph in essay.paragraphs:
        paragraph = paragraph.strip()
        # Filter out titles and sources
        if (
            not (
                paragraph.endswith(".")
                or paragraph.endswith("?")
                or paragraph.endswith("!")
            )
            or paragraph.startswith("https://")
            or len(paragraph.split(" ")) < 6
        ):
            printer.add_text(paragraph)
            continue

        feedback = model.get_feedback(
            comment_author, paragraph, essay_content.split(paragraph)[0]
        )
        printer.add_feedback(comment_author, paragraph, feedback)

    return printer


def init_professor_llama(model_version: int, train: bool) -> ProfessorLlama:
    name_template = "model/professor_llama_v{}"

    max_seq_len = 4015

    return ProfessorLlama(
        name_template.format(model_version),
        max_seq_len,
        train,
        name_template.format(model_version - 1),
    )


def train_professor_llama():
    """
    Trains the model and tests the prompting if enabled
    """
    # NOTE: There needs to be a way to let it know if to not respond to a part or not.
    # - Another thing to try could be to add the requirements
    enable_training = True
    test_prompt = True

    # NOTE: v2 was only trained on paragraph/feedback pairs
    # - v3 is based on v2 and adds student work to the mix,
    # - v4 is based on v3 and adds a placeholder for the current paragraph `____STUDENT_PARAGRAPH____` to save prompt space.
    # - v5 is based on v4 and removes the text following the ____STUDENT_PARAGRAPH____ to have the model give feedback as like it is reading, mimicking human reading
    # - v6 is based on v2 and asjusts the input prompt, the reason to go back to 2 is due to issues with overfitting
    # - v7 is based on base model, and adds context to the point where the model is while reading
    # - v8 is based on v7, but trained a bit longer
    # - v9 is based on v8, but traind a bit longer, as v8 kept hallucinating when giving feedback on one of the essays
    model_version = 9
    model = init_professor_llama(model_version, enable_training)

    data_dir = Path("./data/raw/Student_Submissions/")
    if enable_training:
        print("Training...")
        submissions = load_submissions(data_dir)
        submission_df = process_submissions(submissions)
        model.train_llama(submission_df)
        model.save_model()

    if test_prompt:
        return

    # Prompt the model
    test_document_dir = "./data/unmarked_raw/"
    reqs = parse_requirements("./" + data_dir.joinpath("Requirements.docx").__str__())

    # For every unmarked essay, create feedback to write to disk
    for essay_path_part in os.listdir(test_document_dir):

        printer = get_all_feedback(
            model, test_document_dir + essay_path_part, reqs, COMMENT_AUTHOR
        )
        printer.write_md(f"./feedback/{essay_path_part}.md")


def gradio_llama_demo():
    """
    The demo for the model fine tuning using gradio
    """
    # Init the model to the selected version and disable training
    model = init_professor_llama(9, False)

    # NOTE: This is nested within this function so model can be used below.
    def get_feedback_callback(essay_paths: List[str], requirements_path: str):
        """
        The callback called when the run button is pushed
        """
        n_files = len(essay_paths)
        if n_files > MAX_DEMO_FEEDBACK_BOXES:
            return [
                f"TOO MANY FILES, you can only have a max of: {MAX_DEMO_FEEDBACK_BOXES}"
            ] * MAX_DEMO_FEEDBACK_BOXES

        # Only parse the requirements once
        reqs = parse_requirements(requirements_path)
        feedback_storage = []

        for path in essay_paths:
            printer = get_all_feedback(
                # NOTE: Used here.
                model,
                path,
                reqs,
                COMMENT_AUTHOR,
            )
            feedback_storage.append(printer.__str__())

        # Fill in the document extra empty spaces with placeholders
        if n_files != MAX_DEMO_FEEDBACK_BOXES:
            for _ in range(0, MAX_DEMO_FEEDBACK_BOXES - n_files):
                feedback_storage.append("")

        return feedback_storage

    # Construct the page
    with gr.Blocks(css=MARKDOWN_BOX_CSS) as demo:
        # Title and description
        gr.Markdown(
            "## Professor Llama\nUpload student DOCX files and a single requirements DOCX file to receive structured feedback."
        )

        # The area to upload the essays and the requirements
        with gr.Row():
            docs_input = gr.Files(
                label="Upload Student DOCX Files", file_types=[".docx"]
            )
            req_input = gr.File(label="Upload Requirements DOCX", file_types=[".docx"])

        # The section that handles the feddback previwing
        feedback_containers = []

        # Create the markdown elements to store the feedback
        for _ in range(0, MAX_DEMO_FEEDBACK_BOXES):
            with gr.Column(elem_classes="markdown-box"):
                markdown = gr.Markdown("")
                feedback_containers.append(markdown)

        # Runs the feedback generation
        run_button = gr.Button("Run Feedback Generation")

        run_button.click(
            get_feedback_callback,
            inputs=[docs_input, req_input],
            outputs=feedback_containers,
        )

        # Resets the current documents
        reset_button = gr.Button("Reset Feedback Containers")

        def reset_all():
            return None, None, gr.update(visible=False)

        reset_button.click(reset_all, inputs=[], outputs=[docs_input, req_input])

        # Launches the demo
        demo.launch()
