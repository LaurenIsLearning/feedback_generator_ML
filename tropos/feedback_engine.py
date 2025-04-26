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
  verbose = False, #True will allow to print to console for testing
  max_examples=None #change this WHEN CALLED to tinker with # of examples
):

  #fall back to internal project paths
  requirements_path = requirements_path or "./data/raw/Requirements.docx"
  example_dir = example_dir or "./data/raw"
  target_dir = target_dir or "./data/unmarked_raw"

  if not os.path.exists(output_dir):
        os.makedirs(output_dir)

  examples = load_all_student_examples_recursive(example_dir, requirements_path)
  if max_examples:
    examples = examples[:max_examples]
  #DEBUG
  #print(f"📦 Total examples loaded: {len(examples)}")
  if not examples:
    raise ValueError(f"❌ No examples found in {example_dir}. Make sure it contains .docx files.")

  targets = load_all_targets_recursive(target_dir, requirements_path)
  if not targets:
    raise ValueError(f"❌ No target submissions found in {target_dir}.")

  shared_rubric = examples[0].rubric  # now safe to use!

# ERASE?
#  examples = load_all_student_examples_recursive(example_dir, requirements_path)
#  targets = load_all_targets_recursive(target_dir, requirements_path)
#
#  shared_rubric = examples[0].rubric # assumes at least one example with a good rubric

  for student_name, target in targets:
        target.rubric = shared_rubric 
        prompt = build_prompt(prompt_type, examples, target)
        #DEBUG
        #!!! print(f"\n📜 Prompt for {student_name}:\n{'-'*60}\n{prompt[:3000]}...\n{'-'*60}\n")

        feedback = call_model(prompt, model_name=model)

        #DEBUG
        #print(f"\n🧠 GPT Feedback for {student_name}\n{'='*60}")
        #format_feedback_blocks(feedback)
        #print("="*60 + "\n")

        #DEBUG
        # print("🧪 RUBRIC PORTIONS:", [p["portion"] for p in target.rubric.get_criteria()])

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

        if verbose:
            print(f"--- {prompt_type} Feedback for {filename} ---")
            format_feedback_blocks(feedback)
            print(f"✅ Saved to {output_path}")