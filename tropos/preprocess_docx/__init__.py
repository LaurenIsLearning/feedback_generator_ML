
from docx import Document

from .comments import Comments
from .submission import parse_submission, Submission
from .assignment_requirements import parse_requirements, AssignmentRequirements
from .rubric import parse_rubric, Rubric

#student submission data and requirements

class StudentSubmission:
    def __init__(self, submission_path: str, requirements_path: str) -> None:
        self.rubric = parse_rubric(submission_path)
        self.submission = parse_submission(Document(submission_path))
        self.comments = Comments(submission_path).parse_comments()
        self.assignment_requirements = parse_requirements(requirements_path)

    def to_dict(self):
        return {
            'comments': self.comments.get_results(),
            'rubric': self.rubric.get_criteria(),
            'feedback': self.rubric.get_comments(),
            'assignment_requirements': self.assignment_requirements.get_instructions(),
            'submission_text': self.submission.get_content()
        }
    
    # TODO: Make getters and setters
    #
