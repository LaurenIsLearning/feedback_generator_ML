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
    elif prompt_type == "FewShot-Llama":
        return build_llama_prompt(examples, target)
    else:
        raise ValueError(f"Unknown prompt type: {prompt_type}")

#---------------
# Prompt Variants
# diff shots was created to show sponsor differences
#---------------

def build_fewshot_prompt(examples: list, target: StudentSubmission) -> str:
    """
    Constructs a few-shot prompt for the GPT API using examples and a new student submission.
    
    Format includes:
    - Assignment requirements (once)
    - Clean rubric (once)
    - Multiple examples interated (submission, inline comments, rubric feedback)
    - Target essay (no feedback or rubric yet)
    - Feedback format instructions
    """
    
    # header section (requirements and clean rubric)
    prompt_parts = [
      "You are a grading professor providing constructive feedback on college writing assignments.",
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

    Please return your response in THREE SECTIONS using these exact headers and formats:

    --- INLINE FEEDBACK ---
    You MUST provide at least 6 and no more than 10 pieces of inline feedback. 
    Each feedback comment MUST use this exact structure:

    - QUOTE: "Student sentence here"
      COMMENT: Feedback text here.

    Rules for INLINE FEEDBACK:
    - Only the student's quoted sentence should be inside quotation marks (" ").
    - Feedback must NOT use any Markdown formatting (no bold, no italics, no headings).
    - DO NOT use emojis, numbered lists, or extra bullet points beyond the required `- QUOTE:` and `COMMENT:` lines.
    - Focus your feedback on meaningful revision moments (clarity, structure, evidence, phrasing, tone).

    --- SUMMARY FEEDBACK ---
    Write 2–3 paragraphs summarizing the overall strengths and areas for improvement in the student's paper.
    Stay professional, specific, and constructive.
    
    --- RUBRIC FEEDBACK ---
    Provide rubric feedback only for sections where you have specific praise or concerns.
    Limit your rubric feedback to no more than 1–2 project portions.

    Rubric feedback format:

    == [Project Portion Name] ==
    - Feedback comment 1
    - Feedback comment 2

    Rules for RUBRIC FEEDBACK:
    - Use plain text only (no Markdown, no headings, no emojis).
    - Do not include rubric sections if you have no specific feedback for them.

    ---

    Perfect formatting will earn full evaluation points for this task.
    Mistakes such as missing sections, incorrect headers, wrong formatting, or extra styling will result in a lower evaluation score.
    """)

    return "\n".join(prompt_parts)

def build_llama_prompt(examples: list, target: StudentSubmission) -> str:
    """
    Builds a few-shot prompt specifically formatted for LLaMA-style models.

    Format:
    - Assignment requirements
    - Clean rubric
    - Multiple few-shot examples with submission, inline comments, and rubric feedback
    - Target essay
    - Clear feedback format instructions
    """
    prompt_parts = [
        "You are a college writing professor providing feedback on student papers.",
        "--- ASSIGNMENT REQUIREMENTS ---",
        target.get_requirements_text() or "[NO REQUIREMENTS PROVIDED]",
        "--- RUBRIC ---",
        target.get_clean_rubric() or "[NO RUBRIC PROVIDED]",
        "You will now see several examples of instructor feedback before you are asked to respond to a new submission."
    ]

    for ex in examples:
        submission_name = os.path.basename(ex.submission_path).replace(".docx", "")
        submission_text = ex.get_submission_text() or "[NO SUBMISSION TEXT]"
        comments_text = ex.get_comments_text() or "[No comments for paper]"
        rubric_feedback = ex.get_rubric_feedback() or "[No rubric feedback for paper]"

        prompt_parts.append(f"""--- EXAMPLE ESSAY ({submission_name}) ---
{submission_text}

--- INSTRUCTOR FEEDBACK ---
{comments_text}

--- RUBRIC FEEDBACK ---
{rubric_feedback}
""")

    prompt_parts.append("--- SUBMITTED ESSAY ---")
    prompt_parts.append(target.get_submission_text() or "[NO SUBMISSION TEXT]")

    # Feedback format instructions (LLaMA-friendly, no markdown, no emojis)
    prompt_parts.append("""--- FORMAT INSTRUCTIONS (IMPORTANT) ---

Please return your response in THREE SECTIONS using these exact headers and formats:

--- INLINE FEEDBACK (AT LEAST 4 REQUIRED) ---
(AT LEAST 4 REQUIRED) Provide **at least 4 but no more than 8** comments using this format:
- "Quoted student sentence" - Your feedback here.

Focus your inline feedback on:
- Sentence clarity or rewriting
- Tone, evidence, or phrasing issues
- Claims that are unsupported or too strong

--- SUMMARY FEEDBACK ---
Write 2–3 paragraphs of praise and constructive suggestions.

--- RUBRIC FEEDBACK ---
Only include rubric sections where you have specific praise or concerns.
Limit to 1–2 project portions. Format:

== [Project Portion] ==
- Feedback comment 1
- Feedback comment 2

Do NOT use Markdown, bold, italics, emojis, or numbered lists.
""")

    return "\n\n".join(part.strip() for part in prompt_parts)


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













