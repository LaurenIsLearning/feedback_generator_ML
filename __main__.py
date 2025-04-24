# main function to test local/notebook setup
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
    model_version = 8

    name_template = "model/professor_llama_v{}"

    max_seq_len = 4015

    # Loads, trains and saves the model.
    model = ProfessorLlama(
        name_template.format(model_version),
        max_seq_len,
        train,
        name_template.format(model_version - 1),
    )
    data_dir = Path("./data/raw/")
    if train:
        print("Training...")
        submissions = load_submissions(data_dir)
        submission_df = process_submissions(submissions)
        model.train_llama(submission_df)
        model.save_model()

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


def main():
    # run_feedback_batch(
    #     prompt_type="FewShot",
    #     model="gpt-4o",
    #     requirements_path="./data/raw/Requirements.docx",
    #     example_dir="./data/raw",
    #     target_dir="./data/unmarked_raw",
    #     output_dir="./data/generated_output",
    #     verbose=True
    # )
    test_professor_llama()


if __name__ == "__main__":
    main()
