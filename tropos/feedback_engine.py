from tropos.models.model_router import call_model
from tropos.models.prompt_builder import build_prompt
from utils.student_loader import load_all_student_examples_recursive, load_all_targets_recursive
from tropos.docx_writer import write_feedback_to_docx
from utils.feedback_formatting import format_feedback_blocks
import os
import traceback

#Core feedback generation logic
#making fewshot and gpt-4o as default for now (its best so far)
#THIS IS DEFAULT, DONT CHANGE THIS PLS TY <3
#change in notebook or wherever you call it with your own parameters
def run_feedback_batch(
  prompt_type="FewShot",
  model="gpt-4o", 
  requirements_path=None,
  example_dir=None,
  target_dir=None,
  output_dir="./data/generated_output",
  output_mode="none", #"pretty", "raw", or "none"
  max_examples=None, #change this WHEN CALLED to tinker with # of examples
  profile_text=None
):

  #fall back to internal project paths
  requirements_path = requirements_path or "./data/raw/Requirements.docx"
  example_dir = example_dir or "./data/raw"
  target_dir = target_dir or "./data/unmarked_raw"

  #will create output_dir folder if it doesn't exist
  if not os.path.exists(output_dir):
        os.makedirs(output_dir)

  examples = load_all_student_examples_recursive(example_dir, requirements_path)
  if max_examples:
    examples = examples[:max_examples]

  if not examples:
    raise ValueError(f"❌ No examples found in {example_dir}. Make sure it contains .docx files.")

  targets = load_all_targets_recursive(target_dir, requirements_path)
  if not targets:
    raise ValueError(f"❌ No target submissions found in {target_dir}.")

  shared_rubric = examples[0].rubric  # now safe to use!


  for student_name, target in targets:
        target.rubric = shared_rubric 
        if prompt_type == "ProfileShot":
          prompt = build_prompt(prompt_type, examples=None, target=target, profile_text=profile_text)
        else:
          prompt = build_prompt(prompt_type, examples, target)
        feedback = call_model(prompt, model_name=model)

        # Extract rubric feedback and inject it into target rubric
        if "--- RUBRIC FEEDBACK ---" in feedback:
            try:
                _, rubric_text = feedback.split("--- RUBRIC FEEDBACK ---", 1)
                target.rubric.inject_model_feedback(rubric_text)
            except Exception as e:
                print(f"⚠️ Could not inject rubric feedback for {student_name}: {e}")
        
        filename = os.path.splitext(os.path.basename(target.submission_path))[0]
        safe_model_name = model.replace("/", "_")
        output_path = os.path.join(output_dir, f"{filename}_{safe_model_name}.docx")

        write_feedback_to_docx(
            submission_path=target.submission_path,
            feedback_text=feedback,
            output_path=output_path,
            target = target #this is the full StudentSubmission class info parsed
        )

        #output control
        if output_mode != "none":
            print(f"--- {prompt_type} Feedback for {filename} ---")
            if output_mode == "pretty":
              format_feedback_blocks(feedback)
            elif output_mode == "raw":
              print(feedback)
            else:
              raise ValueError(f"❌ Invalid output_mode '{output_mode}'. Must be 'pretty', 'raw', or 'none'.")
            print(f"✅ Saved to {output_path}")