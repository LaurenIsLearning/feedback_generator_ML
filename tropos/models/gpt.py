import openai

#---------------
# Build Prompt
#---------------
def build_feedback_prompt(student_example: "StudentSubmission", student_target: "StudentSubmission"):
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

    📌 Assignment Requirements:
    {assignment_instructions}

    📋 Rubric:
    {rubric_text}

    📄 Example Essay:
    {example_essay}

    🧑‍🏫 Instructor Feedback:
    {example_comments}
    
    ---

    📄 New Essay:
    {target_essay}

    🧑‍🏫 Please provide feedback for this student as if you were the same instructor. Use the rubric and requirements to guide your response.

    Provide:
    1. Inline Feedback – quote or summarize the parts being addressed and comment on them
    2. Summary Feedback – praise strengths, then list 2–3 clear areas to improve
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

