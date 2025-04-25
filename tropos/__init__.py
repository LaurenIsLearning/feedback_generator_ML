# to run feedback in console and call to notebook

from tropos.feedback_engine import run_feedback_batch

# For testing from console or Colab
def test_feedback_console(
    prompt_type="FewShot",
    model="gpt-4o",
    requirements_path="./data/raw/Requirements.docx",
    example_dir="./data/raw",
    target_dir="./data/unmarked_raw",
    output_dir="./data/generated_output",
    verbose=True,
    max_examples=None
):
    run_feedback_batch(
        prompt_type=prompt_type,
        model=model,
        requirements_path=requirements_path,
        example_dir=example_dir,
        target_dir=target_dir,
        output_dir=output_dir,
        verbose=verbose,
        max_examples=max_examples
    )

def main():
    # Local dev version — fallback to default
    test_feedback_console()

__all__ = ["test_feedback_console", "main"]
