from spire.doc import *
from spire.doc.common import *

# NOTE: The dot notates its within the current directory
from tropos.ui import make_ui
from tropos.docx import StudentSubmission


# Starts the program
if __name__ == "__main__":
    # Tests the ui
    # make_ui()

    # Tests the docx data extraction

    requirements_doc = Document()
    requirements_doc.LoadFromFile("./data/sample1/AssignmentRequirements.docx")

    submission_doc = Document()
    requirements_doc.LoadFromFile("./data/sample1/StudentSubmission.docx")

    print("Testing StudentSubmission class")
    StudentSubmission(submission_doc, requirements_doc)
