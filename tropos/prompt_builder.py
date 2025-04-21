#builds prompts for all models

from tropos.preprocess_docx import StudentSubmission

# Build prompt with below variants
def build_prompt(prompt_type: str, examples: list, target: StudentSubmission):
    if prompt_type == "ZeroShot":
        return build_zeroshot_prompt(target)
    elif prompt_type == "OneShot":
        return build_oneshot_prompt(examples[0], target)
    elif prompt_type == "FewShot":
        return build_fewshot_prompt(examples, target)
    else:
        raise ValueError(f"Unknown prompt type: {prompt_type}")

#---------------
# Prompt Variants
# diff shots was created to show sponsor differences
#---------------

def build_zeroshot_prompt(target: StudentSubmission):
    return f"""
    You are a college writing professor providing feedback on student papers.

    📌 Assignment Requirements:
    {target.get_requirements_text()}

    📋 Rubric:
    {target.rubric.format_clean_only()}

    📄 Student Essay:
    {target.get_submission_text()}

    🧑‍🏫 Please provide feedback using this format:
    - "Quoted student sentence" – Your feedback in plain English.

    Summary Feedback:
    At the end of your response, include a section labeled 'Summary Feedback:' with 2–3 paragraphs of praise and suggestions for improvement.

    ⚠️ Only use the format: - "Quoted student sentence" – feedback
    Do not use Markdown (no **bold** or _italic_), emojis, or numbered lists.
    """

def build_oneshot_prompt(student_example: "StudentSubmission", student_target: "StudentSubmission"):
    #few shot prompting
    rubric_text = student_example.rubric.format_clean_and_feedback()
    assignment_instructions = student_example.get_requirements_text()
    example_essay = student_example.get_submission_text()
    example_comments = student_example.get_comments_text()
    target_essay = student_target.get_submission_text()

    return f"""
    You are a college writing professor providing feedback on student papers.
  
    Use the rubric and assignement requirements below to understand the objective expectations for the assignment.
  
    Below is an example of an assignment with a rubric, student essay, and instructor feedback. Use it as a reference to write feedback on a new student essay that follows the same assignment.   

    ---

    📄 Example Essay:
    {example_essay}

    🧑‍🏫 Instructor Feedback:
    {example_comments}

    📌 Assignment Requirements:
    {assignment_instructions}

    📋 Rubric:
    {rubric_text}
    
    ---

    📄 New Essay:
    {target_essay}

    🧑‍🏫 Please provide feedback using this format:
    - "Quoted student sentence" – Your feedback in plain English.

    Summary Feedback:
    At the end of your response, include a section labeled 'Summary Feedback:' with 2–3 paragraphs of praise and suggestions for improvement.

    ⚠️ Only use the format: - "Quoted student sentence" – feedback
    Do not use Markdown (no **bold** or _italic_), emojis, or numbered lists.
    """

def build_fewshot_prompt(examples: list, target: StudentSubmission):
    few_shot_blocks = ""

    for i, ex in enumerate(examples):
        submission_text = ex.get_submission_text()
        comments_text = ex.get_comments_text()
        rubric_feedback = ex.get_rubric_feedback()

        if not submission_text.strip():
            print(f"[WARNING] Example {i+1} has empty submission text.")

        few_shot_blocks += f"""
      📄 Example Essay:
      {submission_text or '[NO SUBMISSION TEXT]'}

      🧑‍🏫 Instructor Feedback:
      {comments_text or '[No comments for paper]'}

      📋 Rubric Feedback:
      {rubric_feedback or '[No rubric feedback for paper]'}
      """


    # print("DEBUG: Final few-shot block content:\n", few_shot_blocks[:500])

    return f"""
      You are a college writing professor providing feedback on student papers.

      📌 Assignment Requirements:
      {target.get_requirements_text()}

      📋 Rubric:
      {target.get_clean_rubric()}

      {few_shot_blocks}

      ---

      📄 New Essay:
      {target.get_submission_text()}

      🧑‍🏫 Please provide feedback using this format:
      - "Quoted student sentence" – Your feedback in plain English.

      Summary Feedback:
      At the end of your response, include a section labeled 'Summary Feedback:' with 2–3 paragraphs of praise and suggestions for improvement.

      ⚠️ Only use the format: - "Quoted student sentence" – feedback
      Do not use Markdown (no **bold** or _italic_), emojis, or numbered lists.
      """
