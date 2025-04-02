# from spire.doc import *
# from spire.doc.common import *
from docx import Document

from .comments import parse_comments, Comments
from .submission import parse_submission, Submission
from .requirements import parse_requirements, Requirements
from .rubric import parse_rubric, extract_highlighted_phrases, Rubric

#student submission data and requirements

class StudentSubmission:

    rubric: Rubric
    """
    The rubric table at the bottom of the submission document 
    """

    comments: Comments
    """
    The inline comments 
    """

    requirements: Requirements
    """
    The requirements file 
    """

    submission: Submission
    """
    The students written work
    """

    def __init__(self, submission: str, requirements: str) -> None:
        self.rubric = parse_rubric(submission)
        self.submission = parse_submission(submission)
        self.comments = parse_comments(submission)
        self.requirements = requirements(Document(requirements_path))
        

    # TODO: Make getters and setters
    #