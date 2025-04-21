from tropos.models.model_router import call_model
from tropos.models.prompt_builder import build_prompt
from utils.student_loader import load_all_student_examples_recursive, load_all_targets_recursive
from tropos.docx_writer import write_feedback_to_docx
from utils.feedback_formatting import format_feedback_blocks
import os

#Core feedback generation logic
#making fewshot and gpt-4o as default for now (its best so far)
def run_feedback_batch(
  prompt_type="FewShot",
  model="gpt-4o", requirements_path=None,
  example_dir=None,
  target_dir=None,
  output_dir="./data/generated_output",
  verbose = False #True will allow to print to console for testing
):

  #fall back to internal project paths
  requirements_path = requirements_path or "./data/raw/Requirements.docx"
  example_dir = example_dir or "./data/raw"
  target_dir = target_dir or "./data/unmarked_raw"

  if not os.path.exists(output_dir):
        os.makedirs(output_dir)

  examples = load_all_student_examples_recursive(example_dir, requirements_path)
  targets = load_all_targets_recursive(target_dir, requirements_path)

  for student_name, target in targets:
        prompt = build_prompt(prompt_type, examples, target)
        print(prompt)
        feedback = call_model(prompt, model_name=model)

        filename = os.path.splitext(os.path.basename(target.submission_path))[0]
        output_path = os.path.join(output_dir, f"{filename}_{model}.docx")

        write_feedback_to_docx(
            submission_path=target.submission_path,
            feedback_text=feedback,
            output_path=output_path
        )

        if verbose:
            print(f"--- {prompt_type} Feedback for {filename} ---")
            format_feedback_blocks(feedback)
            print(f"✅ Saved to {output_path}")