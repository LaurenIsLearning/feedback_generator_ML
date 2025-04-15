import openai

#---------------
# Build Prompt
#---------------
def build_feedback_prompt(student_example: "StudentSubmission", student_target: "StudentSubmission"):
    #few shot prompting
    rubric_text = student_example.get_rubric_prompt()
    assignment_instructions = student_example.get_requirements_text()
    example_essay = student_example.get_submission_text()
    example_comments = student_example.get_comments_text()
    target_essay = student_target.get_submission_text()

    return f"""
    You are a writing instructor grading student essays.

    Assignment Instructions:
    {assignment_instructions}

    Rubric:
    {rubric_text}

    --- Example Submission ---
    Student Essay:
    {example_essay}

    Instructor Feedback:
    {example_comments}

    --- New Submission ---
    Student Essay:
    {target_essay}

    Please provide inline feedback (as if commenting on the text) and then write a brief summary highlighting strengths and areas for improvement.
    """

# --------------------------
# ChatGPT API Caller
# --------------------------
def call_chatgpt(prompt: str, model="gpt-4", temperature=0.7, max_tokens=1500) -> str:
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

