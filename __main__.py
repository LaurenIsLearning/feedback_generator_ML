# main function to test local/notebook setup
from docx import Document
from tropos.feedback_engine import run_feedback_batch

def main():
    run_feedback_batch(
        prompt_type="FewShot",
        model="gpt-4o",
        requirements_path="./data/raw/Requirements.docx",
        example_dir="./data/raw",
        target_dir="./data/unmarked_raw",
        output_dir="./data/generated_output",
        verbose=True
    )