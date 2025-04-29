#builds prompts for all models
import os
from tropos.preprocess_docx import StudentSubmission
from typing import List
from tropos.models.model_router import call_model
from utils.student_loader import load_all_student_examples_recursive


# Build prompt with below variants
def build_prompt(prompt_type: str, examples: list, target: StudentSubmission, profile_text: str = None):
    if prompt_type == "ZeroShot":
        return build_zeroshot_prompt(target)
    elif prompt_type == "OneShot":
        return build_oneshot_prompt(examples[0], target)
    elif prompt_type == "FewShot":
        return build_fewshot_prompt(examples, target)
    elif prompt_type == "FewShot-Llama":
        return build_llama_prompt(examples, target)
    elif prompt_type == "ProfileShot":
        if not profile_text:
            raise ValueError("ProfileShot requires profile_text parameter.")
        return build_profile_based_prompt(profile_text, target)
    else:
        raise ValueError(f"Unknown prompt type: {prompt_type}")

# ---------------
# Generate Instructor Profile Builder
# ---------------


# Batch examples into smaller groups
def batch_examples(examples: List, batch_size: int = 5) -> List[List]:
    return [examples[i:i+batch_size] for i in range(0, len(examples), batch_size)]

# Build a prompt for a batch of examples
def build_batch_prompt(batch_examples: List) -> str:
    parts = [
        "You are helping create a Feedback Profile for a college writing instructor.",
        "Below are several examples of student submissions, instructor inline comments, and rubric feedback.",
        "Analyze the examples and summarize the instructor's feedback habits, tone, priorities, and style."
    ]

    for ex in batch_examples:
        submission_name = os.path.basename(ex.submission_path).replace(".docx", "")
        submission_text = ex.get_submission_text()
        comments_text = ex.get_comments_text()
        rubric_feedback = ex.get_rubric_feedback()

        parts.append(f"""
--- EXAMPLE ({submission_name}) ---
Student Submission:
{submission_text or '[NO SUBMISSION TEXT]'}

Instructor Inline Feedback:
{comments_text or '[No comments for paper]'}

Rubric Feedback:
{rubric_feedback or '[No rubric feedback for paper]'}
""")
    return "\n".join(parts)

# Generate a mini profile for a batch
def generate_mini_profile(batch_examples: List, model_name="gpt-4o") -> str:
    prompt = build_batch_prompt(batch_examples)
    response = call_model(prompt, model_name=model_name)
    return response.strip()

# FULL Instructor Profile Builder
def generate_full_instructor_profile(
    examples_dir: str,
    requirements_path: str,
    batch_size: int = 5,
    model_name: str = "gpt-4o",
    debug: bool = False
) -> str:
    examples = load_all_student_examples_recursive(examples_dir, requirements_path, verbose=False)

    print(f"📦 Loaded {len(examples)} examples")
    #for ex in examples:
    #    print(f"✅ Example loaded: {ex.submission_path}")
    #
    #if not examples:
    #    raise ValueError("❌ No examples found in directory.")

    mini_profiles = []

    for idx, batch in enumerate(batch_examples(examples, batch_size=batch_size)):
        if debug:
            print(f"🔹 Processing Batch {idx + 1} ({len(batch)} examples)")

        mini_profile = generate_mini_profile(batch, model_name=model_name)

        if debug:
            print(f"📝 Mini Profile {idx + 1}:\n{mini_profile}\n{'-'*40}\n")

        mini_profiles.append(mini_profile.strip())

    if debug:
        print("🔧 Merging mini profiles into the final Instructor Profile...\n")

    merge_prompt = f"""
You are a writing professor trainer.

Below are multiple mini-profiles describing an instructor's feedback style.

Please synthesize them into a single coherent Instructor Feedback Profile. 
Highlight common patterns, tone, priorities, and minimize contradictions.

---
{chr(10).join(mini_profiles)}
---
"""

    final_profile = call_model(merge_prompt, model_name=model_name)

    if debug:
        print("✅ Final Instructor Profile Generated:\n")
        print(final_profile)
        print("\n" + "="*80 + "\n")

    return final_profile.strip()

# Load a saved profile
def load_profile_from_txt(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Profile file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        profile = f.read()

    return profile.strip()

# ---------------
# Prompt Variants
# diff shots was created to show sponsor differences
# ---------------

##------- few shot using FULL instructor profile
def build_profile_based_prompt(profile_text: str, target: 'StudentSubmission') -> str:
    """
    Constructs a prompt using a prebuilt instructor profile instead of re-including full examples.
    """

    prompt_parts = [
        "You are a college writing professor providing feedback on student papers.",
        "\n--- INSTRUCTOR FEEDBACK PROFILE ---",
        profile_text,
        "\n--- ASSIGNMENT REQUIREMENTS ---",
        target.get_requirements_text(),
        "\n--- RUBRIC ---",
        target.get_clean_rubric(),
        "\n--- SUBMITTED ESSAY ---",
        target.get_submission_text(),
        "\n--- FORMAT INSTRUCTIONS (IMPORTANT) ---",
        
        """
        Please return your response in THREE SECTIONS using these exact headers:

        --- INLINE FEEDBACK (AT LEAST 4 REQUIRED) ---
        Provide 4–8 inline comments:
        - "Quoted student sentence" – Your feedback.

        --- SUMMARY FEEDBACK ---
        Write 2–3 paragraphs of overall praise and suggestions.

        --- RUBRIC FEEDBACK ---
        Comment on only 1–2 rubric sections.
        Use this format:
        == [Project Portion] ==
        - Comment 1
        - Comment 2

        Do NOT use Markdown (no bold, italics, headers).
        Keep comments supportive but constructive.
        """
    ]

    return "\n".join(prompt_parts)



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

    Please return your response in THREE SECTIONS using these exact headers and formats:

    --- INLINE FEEDBACK (AT LEAST 4 REQUIRED) ---
    (AT LEAST 4 REQUIRED) Provide **at least 4 but no more than 8** comments using this format:
    - "Quoted student sentence" – Your feedback here.

    Focus your inline feedback on moments where:
    - A sentence could be clarified or rewritten
    - Tone, evidence, or phrasing need revision
    - Claims are unsupported or overly strong

    --- SUMMARY FEEDBACK ---
    Write 2–3 paragraphs of praise and constructive suggestions.

    
    --- RUBRIC FEEDBACK ---
    Only include rubric sections where you have specific praise or concerns. **Limit your comments to 1–2 project portions**.

    Rubric Format:
    == [Project Portion] ==
    - Feedback comment 1
    - Feedback comment 2

    Do NOT use Markdown (no bold, italics, headers), emojis, or numbered lists.
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

--- INLINE FEEDBACK ---
Provide **at least 4 but no more than 8** comments using this format:
- "Quoted student sentence" – Your feedback here.

Focus your inline feedback on:
- Sentence clarity or rewriting
- Tone, evidence, or phrasing issues
- Claims that are unsupported or too strong

--- SUMMARY FEEDBACK ---
(REQUIRED) Write 2–3 paragraphs of praise and constructive suggestions.

--- RUBRIC FEEDBACK ---
(REQUIRED) Only include rubric sections where you have specific praise or concerns.
Limit to 1–2 project portions. Format:

--- [Project Portion] ---
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


def build_oneshot_prompt(
    student_example: "StudentSubmission", student_target: "StudentSubmission"
):
    # few shot prompting
    rubric_text = student_example.rubric.format_clean_and_feedback()
    assignment_instructions = student_example.get_requirements_text()
    example_essay = student_example.get_submission_text()
    example_comments = student_example.get_comments_text()
    target_essay = student_target.get_submission_text()

    return f"""
    You are a college writing professor providing feedback on student papers.
  
    Use the rubric and assignment requirements below to understand the objective expectations for the assignment.
  
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











