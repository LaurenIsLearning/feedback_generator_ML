from tropos import StudentSubmission
import openai
import time
from openai.error import RateLimitError

#---------------
# Prompt Variants
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
    - "Quoted sentence" – Your comment.

    Include a 'Summary Feedback:' section at the end.
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

    🧑‍🏫 Please provide feedback for this student as if you were the same instructor. Use the rubric and requirements to guide your response.

    Provide:
    1. Inline feedback: For each piece of inline feedback, use the format:
      - "Quoted student sentence" – Your feedback in plain English.

    2. Summary Feedback – At the end, provide a 'Summary Feedback:' section, starting with that exact heading, followed by 2–3 paragraphs of general praise and suggestions.
    """

def build_fewshot_prompt(examples: list, target: StudentSubmission):
    few_shot_blocks = ""
    for ex in examples:
        few_shot_blocks += f"""
      📄 Example Essay:
      {ex.get_submission_text()}

      🧑‍🏫 Instructor Feedback:
      {ex.get_comments_text()}
      """
    return f"""
      You are a college writing professor providing feedback on student papers.

      📌 Assignment Requirements:
      {target.get_requirements_text()}

      📋 Rubric:
      {target.rubric.format_clean_and_feedback()}

      {few_shot_blocks}

      ---

      📄 New Essay:
      {target.get_submission_text()}

      🧑‍🏫 Please provide feedback for this student as if you were the same instructor. Use the rubric and requirements to guide your response.

      Provide:
      1. Inline feedback: For each piece of inline feedback, use the format:
        - "Quoted student sentence" – Your feedback in plain English.

      2. Summary Feedback – At the end, provide a 'Summary Feedback:' section, starting with that exact heading, followed by 2–3 paragraphs of general praise and suggestions.
      """

# --------------------------
# ChatGPT API Caller
# --------------------------

def call_chatgpt(prompt: str, model="gpt-4o", temperature=0.7, max_tokens=1500, retries=3) -> str:
    # Estimate token usage for throttling (prompt words + expected output)
    estimated_tokens = len(prompt.split()) + max_tokens
    tokens_per_second = 300000 / 60  # For gpt-4o
    sleep_time = estimated_tokens / tokens_per_second

    for attempt in range(retries):
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a college writing professor providing detailed feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except RateLimitError as e:
            wait = max(sleep_time, (2 ** attempt))  # backoff or token-based wait
            print(f"⚠️ Rate limit hit. Waiting {wait:.1f} seconds before retrying...")
            time.sleep(wait)

    raise RuntimeError("❌ Failed after multiple retries due to rate limits.")

def call_chatgpt2(prompt: str, model="gpt-4o", temperature=0.7, max_tokens=1500. retries = 3) -> str:
    response = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a college writing professor providing detailed feedback."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

# --------------------------
# Public API: Generate Feedback
# --------------------------
def generate_feedback(student_example: "StudentSubmission", student_target: "StudentSubmission") -> str:
    prompt = build_feedback_prompt(student_example, student_target)
    return call_chatgpt(prompt)

