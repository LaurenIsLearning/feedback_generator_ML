# This file marks tropos as a Python package.

from .models.gpt import generate_feedback
from .models.trained import load_model

from .preprocess_docx.rubric import parse_rubric
from .preprocess_docx.submission import parse_submission
from .preprocess_docx.requirements import parse_requirements
from .preprocess_docx.comments import parse_comments

# Optional UI export
from .gradio.ui import launch_ui