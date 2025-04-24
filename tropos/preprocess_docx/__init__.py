from typing_extensions import Union
from docx import Document

from .comments import Comments
from .submission import parse_submission, Submission
from .rubric import parse_rubric, Rubric

# student submission data and requirements


class StudentSubmission:
    rubric: Rubric
    """
    The rubric table at the bottom of the submission document 
    """

    comments: Comments
    """
    The inline comments 
    """

    assignment_requirements: AssignmentRequirements
    """
    The requirements file 
    """

    submission: Submission
    """
    The students written work
    """

    def __init__(
        self, submission_path: str, requirements: Union[str, AssignmentRequirements]
    ) -> None:
        self.submission_path = submission_path
        self.requirements_path = requirements
        self.rubric = parse_rubric(submission_path)
        self.submission = parse_submission(Document(submission_path))
        self.comments = Comments(submission_path).parse_comments()

        # NOTE: This is not likely the best way to accomplish this, rather it is what it is right now

        if isinstance(requirements, str):

            self.assignment_requirements = parse_requirements(requirements)
            return
        if isinstance(requirements, AssignmentRequirements):

            self.assignment_requirements = requirements
            return
        # Input validation just in case there is an issue
        raise RuntimeError(
            f'❌ Failed to load requirements as the type does not match "str" or "AssignmentRequirements", found: {err}'
        )

    # -----------------------------------------------
    # utility methods to use directly in prompting
    # -----------------------------------------------
    # returns rubric formatted as readable text for prompts
    def get_clean_rubric(self) -> str:
      return self.rubric.format_clean_only() if self.rubric else ""

    def get_rubric_feedback(self) -> str:
        return self.rubric.format_rubric_feedback() if self.rubric else ""

    # returns students written essay content
    def get_submission_text(self) -> str:
        return self.submission.get_content() if self.submission else ""

    # returns inline feedback as flat string with one comment per line
    def get_comments_text(self) -> str:
        if not self.comments:
            return ""
        return "\n".join(
            f"- {c['comment_text']} (about: '{c['commented_text']}')"
            for c in self.comments.get_results()
        )

    # returns assignment instructions as plain text
    def get_requirements_text(self) -> str:
        return (
            self.assignment_requirements.get_instructions()
            if self.assignment_requirements
            else ""
        )

    # returns all relevant data in one dictionary (debug and export)
    def get_all(self) -> dict:
        return {
            "rubric": self.get_rubric_prompt(),
            "submission": self.get_submission_text(),
            "comments": self.get_comments_text(),
            "requirements": self.get_requirements_text(),
        }


__all__ = [
    "StudentSubmission",
    "AssignmentRequirements",
    "Rubric",
    "Submission",
    "Comments",
]
