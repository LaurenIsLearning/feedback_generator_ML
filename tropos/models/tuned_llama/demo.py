import os
from os.path import basename
from pathlib import Path
from typing import List, Tuple

from huggingface_hub.inference._generated.types import document_question_answering
from docx import Document
from tropos.feedback_engine import run_feedback_batch
from tropos.markdown_printer import MarkdownFeedbackPrinter
from tropos.models.tuned_llama import ProfessorLlama, process_submissions
from tropos.preprocess_docx import StudentSubmission
from tropos.preprocess_docx.assignment_requirements import parse_requirements


def load_submissions(data_dir: Path) -> List[StudentSubmission]:
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


def test_professor_llama():
    # NOTE: There needs to be a way to let it know if to not respond to a part or not.
    # - Another thing to try could be to add the requirements
    train = True

    # NOTE: v2 was only trained on paragraph/feedback pairs
    # - v3 is based on v2 and adds student work to the mix,
    # - v4 is based on v3 and adds a placeholder for the current paragraph `____STUDENT_PARAGRAPH____` to save prompt space.
    # - v5 is based on v4 and removes the text following the ____STUDENT_PARAGRAPH____ to have the model give feedback as like it is reading, mimicking human reading
    # - v6 is based on v2 and asjusts the input prompt, the reason to go back to 2 is due to issues with overfitting
    # - v7 is based on base model, and adds context to the point where the model is while reading
    # - v8 is based on v7, but trained a bit longer
    # - v9 is based on v8, but traind a bit longer, as v8 kept hallucinating when giving feedback on one of the essays
    model_version = 9

    name_template = "model/professor_llama_v{}"

    max_seq_len = 4015

    # Loads, trains and saves the model.
    model = ProfessorLlama(
        name_template.format(model_version),
        max_seq_len,
        train,
        name_template.format(model_version - 1),
    )
    data_dir = Path("./data/raw/Student_Submissions/")
    if train:
        print("Training...")
        submissions = load_submissions(data_dir)
        submission_df = process_submissions(submissions)
        model.train_llama(submission_df)
        model.save_model()

    return  # Skip the prompting
    # prompt the model

    test_document_dir = "./data/unmarked_raw/"
    comment_author = "Dr. H"
    reqs = parse_requirements("./" + data_dir.joinpath("Requirements.docx").__str__())

    for essay_path_part in os.listdir(test_document_dir):

        printer = MarkdownFeedbackPrinter(essay_path_part)

        essay = StudentSubmission(test_document_dir + essay_path_part, reqs).submission
        essay_content = essay.get_content()
        print("-----------------------------")
        print("Essay -------")
        print(essay_content)
        print("Feedback -------")
        # TODO: Have this use the same processor as the process_submissions function in the tuned_llama module to keep it consistent
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
        printer.write_md(f"./feedback/{essay_path_part}.md")


def gradio_llama_demo():
    import gradio as gr

    train = False
    model_version = 9

    name_template = "model/professor_llama_v{}"

    max_seq_len = 4015

    model = ProfessorLlama(
        name_template.format(model_version),
        max_seq_len,
        train,
        name_template.format(model_version - 1),
    )

    with gr.Blocks(
        css=""".markdown-box {
    border: 1px solid #aaa;
    padding: 12px;
    border-radius: 6px;
    background-color:  #52525b;
    display: block;
    margin: 10px 0;
}"""
    ) as demo:

        gr.Markdown(
            "## Professor Llama\nUpload student DOCX files and a single requirements DOCX file to receive structured feedback."
        )

        with gr.Row():
            docs_input = gr.Files(
                label="Upload Student DOCX Files", file_types=[".docx"]
            )
            req_input = gr.File(label="Upload Requirements DOCX", file_types=[".docx"])

        run_btn = gr.Button("Run Feedback")
        reset_btn = gr.Button("Reset")

        feedback_containers = []

        MAX_DOCS = 10

        for i in range(0, MAX_DOCS):
            with gr.Column(elem_classes="markdown-box"):
                markdown = gr.Markdown("")
                feedback_containers.append(markdown)

        def generate_feedback(files, requirements_doc):

            n_files = len(files)
            if n_files > MAX_DOCS:
                return [
                    f"TOO MANY FILES, can only have a max of: {MAX_DOCS}"
                ] * MAX_DOCS

            reqs = parse_requirements(requirements_doc)
            comment_author = "Dr. H"
            feedbacks = []  # To hold all feedbacks for each file

            for i, file in enumerate(files):
                printer = MarkdownFeedbackPrinter(file)

                essay = StudentSubmission(file, reqs).submission
                essay_content = essay.get_content()

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

                feedbacks.append(printer.__str__())

            if n_files != MAX_DOCS:
                for i in range(0, MAX_DOCS - n_files):
                    feedbacks.append("")

            return feedbacks

        def wrapper(files, req):
            return generate_feedback(files, req)

        def reset_all():
            return None, None, gr.update(visible=False)

        run_btn.click(
            wrapper, inputs=[docs_input, req_input], outputs=feedback_containers
        )
        reset_btn.click(reset_all, inputs=[], outputs=[docs_input, req_input])

        # feedback_container.render()

        demo.launch()
