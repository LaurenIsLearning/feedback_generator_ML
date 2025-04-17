#handles single calls (generate, format, save)

#----- FILLER GPT CODE UNTESTED
#from utils.student_loader import load_all_student_submissions, load_targets
#from tropos.models.prompt_builder import build_prompt
#from tropos.models.model_router import call_model
#from tropos.docx_writer import write_feedback_to_docx
#from utils.feedback_formatting import format_feedback_blocks
#
#example_cache = {}
#
#def load_examples(requirements_path, raw_dir):
#    global example_cache
#    if not example_cache:
#        example_cache = load_all_student_submissions(raw_dir, requirements_path)
#    return example_cache
#
#def generate_feedback(
#    target_submission,
#    prompt_type="FewShot",
#    model_name="gpt",
#    example_source=None,
#    save_path=None,
#    save_docx=True,
#    print_feedback=False
#):
#    if example_source is None:
#        raise ValueError("No example source provided.")
#
#    prompt = build_prompt(prompt_type, example_source, target_submission)
#    feedback = call_model(prompt, model_name=model_name)
#
#    if print_feedback:
#        format_feedback_blocks(feedback, width=80)
#
#    if save_docx and save_path:
#        write_feedback_to_docx(
#            submission_path=target_submission.submission_path,
#            feedback_text=feedback,
#            output_path=save_path
#        )
#
#    return feedback
#