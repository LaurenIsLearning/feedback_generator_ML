#builds prompts for all models
import os
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

def build_fewshot_prompt(examples: list, target: StudentSubmission) -> str:
    """
    Constructs a few-shot prompt for the GPT API using examples and a new student submission.
    
    Format includes:
    - Assignment requirements (once)
    - Clean rubric (once)
    - Multiple examples interated (submission, inline comments, rubric feedback)
    - Target essay (no feedback yet)
    - Feedback format instructions
    """
    
    # header section (requirements and clean rubric)
    prompt_parts = [
      "You are a college writing professor providing feedback on student papers.",
      "\n--- ASSIGNMENT REQUIREMENTS ---",
      target.get_requirements_text(),
      "\n--- RUBRIC ---",
      target.get_clean_rubric()
    ]
    
    # fewshot examples
    for ex in examples:
        submission_name = os.path.basename(ex.submission_path).replace(".docx", "")
        submission_text = ex.get_submission_text()
        comments_text = ex.get_comments_text()
        rubric_feedback = ex.get_rubric_feedback()

        # Warn if any example is missing submission text
        if not submission_text.strip():
             print(f"[WARNING] Example '{submission_name}' has empty submission text.")

        prompt_parts.append(f"""
          --- EXAMPLE ESSAY ({submission_name}) ---
          {submission_text or '[NO SUBMISSION TEXT]'}

          --- INSTRUCTOR FEEDBACK ---
          {comments_text or '[No comments for paper]'}

          --- RUBRIC FEEDBACK ---
          {rubric_feedback or '[No rubric feedback for paper]'}
          """)

    #--- target essay--
    prompt_parts.append("-----")
    prompt_parts.append("\n--- SUBMITTED ESSAY ---")
    prompt_parts.append(target.get_submission_text())

    # Format instructions (match docx_writer.py)
    prompt_parts.append("""
    --- FORMAT INSTRUCTIONS (IMPORTANT) ---

    Please return your response in **three sections** using these exact headers with the exact format given for each header contents:

    --- INLINE FEEDBACK ---
    - "Quoted student sentence" – Your feedback here.

    --- SUMMARY FEEDBACK ---
    Write 2–3 paragraphs of praise and constructive suggestions.

    --- RUBRIC FEEDBACK ---
    Provide one bullet per project portion using these exact project portion names:
    - Introduction
    - Background
    - Analysis
    - Response

    Format:
    - [Project Portion]: [Your feedback]

    Example:
    - Background: The section is well-researched but could include more neutral sources.


    ⚠️ Do not use Markdown (no bold, italics, headers), emojis, or numbered lists.
    """)

    return "\n".join(prompt_parts)












