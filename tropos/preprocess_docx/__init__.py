from docx import Document

from .comments import Comments
from .submission import parse_submission, Submission
from .assignment_requirements import parse_requirements, AssignmentRequirements
from .rubric import parse_rubric, Rubric

#student submission data and requirements

class StudentSubmission:
    cached_requirements = None

    rubric: Rubric
    """
    The rubric table at the bottom of the submission document 
    """
    comments: Comments
    """
    The inline comments 
    """
    requirements: AssignmentRequirements
    """
    The requirements file 
    """
    submission: Submission
    """
    The students written work
    """
    def __init__(self, submission_path: str, requirements_path: str) -> None:
      self.submission_path = submission_path
      self.requirements_path = requirements_path
      self.rubric = parse_rubric(submission_path)
      self.submission = parse_submission(Document(submission_path))
      self.comments = Comments(submission_path).parse_comments()

      # to use cache or parse if provided
      if StudentSubmission.cached_requirements:
        self.assignment_requirements = StudentSubmission.cached_requirements
      elif requirements_path:
        try:
            self.assignment_requirements = parse_requirements(requirements_path)
            StudentSubmission.cached_requirements = self.assignment_requirements
        except Exception as e:
            print(f"❌ Failed to load requirements at {requirements_path}: {e}")
            self.assignment_requirements = None
      else:
        self.assignment_requirements = None

    #-----------------------------------------------
    # utility methods to use directly in prompting
    #-----------------------------------------------
    #returns rubric formatted as readable text for prompts
    def get_rubric_prompt(self) -> str:
      return self.rubric.format_for_prompt() if self.rubric else ""
    
    #returns students written essay content
    def get_submission_text(self) -> str:
      return self.submission.get_content() if self.submission else ""

    #returns inline feedback as flat string with one comment per line
    def get_comments_text(self) -> str:
      if not self.comments:
         return ""
      return "\n".join(
        f"- {c['comment_text']} (about: '{c['commented_text']}')"
        for c in self.comments.get_results()
      )
    
    #returns assignment instructions as plain text
    def get_requirements_text(self) -> str:
      return self.assignment_requirements.get_instructions() if self.assignment_requirements else ""

    #returns all relevant data in one dictionary (debug and export)
    def get_all(self) -> dict:
      return {
        "rubric": self.get_rubric_prompt(),
        "submission": self.get_submission_text(),
        "comments": self.get_comments_text(),
        "requirements": self.get_requirements_text()
      }
