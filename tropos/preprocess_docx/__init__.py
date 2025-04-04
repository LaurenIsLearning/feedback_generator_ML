from docx import Document  

from .comments import parse_comments, Comments
from .submission import parse_submission, Submission
from .requirements import parse_requirements, Requirements
from .rubric import parse_rubric, Rubric

class StudentSubmission:
    """
    Preserves all original docstrings and structure
    Only changed: spire.doc.Document -> docx.Document
    """
    rubric: Rubric
    """The rubric table at the bottom of the submission document"""
    
    comments: Comments
    """The inline comments"""
    
    requirements: Requirements
    """The requirements file"""
    
    submission: Submission
    """The students written work"""

    def __init__(self, submission: Document, requirements: Requirements) -> None:  
        self.rubric = parse_rubric(submission)
        self.submission = parse_submission(submission)
        self.comments = parse_comments(submission)
        self.requirements = requirements

    
    def get_rubric(self) -> Rubric:
        return self.rubric
    
    def get_comments(self) -> Comments:
        return self.comments
    
    def get_requirements(self) -> Requirements:
        return self.requirements
    
    def get_submission(self) -> Submission:
        return self.submission
