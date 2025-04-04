# This file marks tropos as a Python package.

from .models.gpt import generate_feedback
from .models.trained import load_model

from .preprocess_docx.rubric import parse_rubric
from .preprocess_docx.submission import parse_submission
from .preprocess_docx.requirements import parse_requirements
from .preprocess_docx.comments import Comments, parse_comments
from .preprocess_docx import StudentSubmission


# Optional UI export
from .gradio.ui import launch_ui

from spire.doc import *
from spire.doc.common import *



# Starts the program
def main():
    # Tests the ui
    # make_ui()

    # Tests the docx data extraction

    requirements_doc = Document()
    requirements_doc.LoadFromFile(".data/raw/Requirements.docx")

    submission_doc = Document()
    submission_doc.LoadFromFile("data/raw/Student 1/Student 1 Part 1.docx")

    print("Testing StudentSubmission class")
    StudentSubmission(submission_doc, requirements_doc)
