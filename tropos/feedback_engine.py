from tropos.models.model_router import call_model
from tropos.models.prompt_builder import build_prompt
from utils.student_loader import load_all_student_examples_recursive, load_all_targets_recursive
from tropos.docx_writer import write_feedback_to_docx
from utils.feedback_formatting import format_feedback_blocks
import os
import traceback
from tropos.preprocess_docx.rubric import parse_rubric

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
    output_mode="none",
    max_examples=None,
    profile_text=None
):

    # Fallback default paths
    requirements_path = requirements_path or "./data/raw/Requirements.docx"
    example_dir = example_dir or "./data/raw"
    target_dir = target_dir or "./data/unmarked_raw"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    examples = None

    if prompt_type != "ProfileShot":
        examples = load_all_student_examples_recursive(example_dir, requirements_path)
        if max_examples:
            examples = examples[:max_examples]

        if not examples:
            raise ValueError(f"❌ No examples found in {example_dir}. Make sure it contains .docx files.")

        shared_rubric = examples[0].rubric
    else:
        # 👈 NEW: Load rubric manually if ProfileShot
        shared_rubric = parse_rubric(requirements_path)

    targets = load_all_targets_recursive(target_dir, requirements_path)
    if not targets:
        raise ValueError(f"❌ No target submissions found in {target_dir}.")

    for student_name, target in targets:
        target.rubric = shared_rubric

        if prompt_type == "ProfileShot":
            prompt = build_prompt(prompt_type, examples=None, target=target, profile_text=profile_text)
        else:
            prompt = build_prompt(prompt_type, examples, target)

        feedback = call_model(prompt, model_name=model)

        # Inject rubric feedback
        if "--- RUBRIC FEEDBACK ---" in feedback:
          try:
            _, rubric_text = feedback.split("--- RUBRIC FEEDBACK ---", 1)
            if target.rubric:  # 🛡️ Prevent NoneType crash
              target.rubric.inject_model_feedback(rubric_text)
            else:
              print(f"⚠️ target.rubric is None for {student_name}. Cannot inject rubric feedback.")
          except Exception as e:
            print(f"⚠️ Could not inject rubric feedback for {student_name}: {e}")

        filename = os.path.splitext(os.path.basename(target.submission_path))[0]
        safe_model_name = model.replace("/", "_")
        safe_prompt_type = prompt_type.replace("/", "_")
        output_path = os.path.join(output_dir, f"{filename}_{safe_prompt_type}_{safe_model_name}.docx")

        write_feedback_to_docx(
            submission_path=target.submission_path,
            feedback_text=feedback,
            output_path=output_path,
            target=target,
        )

        # Optional output control
        if output_mode != "none":
            print(f"--- {prompt_type} Feedback for {filename} ---")
            if output_mode == "pretty":
                format_feedback_blocks(feedback)
            elif output_mode == "raw":
                print(feedback)
            else:
                raise ValueError(f"❌ Invalid output_mode '{output_mode}'. Must be 'pretty', 'raw', or 'none'.")
            print(f"✅ Saved to {output_path}")