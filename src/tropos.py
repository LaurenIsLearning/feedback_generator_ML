# !pip install openai gradio
import openai
import gradio as gr

# Memory and feedback storage
import json
import os
import re
import shared
from shared import OutputFields
from shared import InputFields

from google.colab import userdata

# Obtain chatbot API
openai.api_key = userdata.get("ChatGPT")
TEMPERATURE = 0.7
OPEN_AI_MODEL = "gpt-4o"

"""# Memory and feedback storage to CSV"""

## Future implementation, too complicated for this moment. using json cache for now

"""# Assignment Requirements w/Cache"""

# Requirements summary cache (to avoid multiple API calls)
REQUIREMENTS_CACHE_FILE = "requirements_cache.json"


def load_cache():
    """Load the requirements cache from a file"""
    if os.path.exists(REQUIREMENTS_CACHE_FILE):
        with open(REQUIREMENTS_CACHE_FILE, "r") as file:
            return json.load(file)
    return {}


def save_cache(cache):
    """Save the requirements cache to a file"""
    with open(REQUIREMENTS_CACHE_FILE, "w") as file:
        json.dump(cache, file)


# Retrieve or create the requirements
def get_or_store_requirements(assignment_id: str, requirements_text: str):
    """Retrieve a cached summary or generate a new one if missing"""

    # Validate if assignment_id is given
    if not assignment_id.strip():
        return "**Error:** Missing assignment ID. Please enter a valid assignment ID."

    cache = load_cache()
    cache_key = f"{assignment_id}_requirements"

    # Return cached requirements if available
    if cache_key in cache and cache[cache_key]:
        return cache[cache_key]

    # Ensure the requirements text is not empty
    if not requirements_text.strip():
        return "--No assignment requirements provided."

    # Store it in the cache
    cache[cache_key] = requirements_text
    save_cache(cache)

    return requirements_text  # Returns the requirements


"""# Generate Inline Feedback"""


# Generate inline feedback
def generate_inline_feedback(input: InputFields):
    """
    Processes the full essay, compares it to assignment requirements, and provides inline feedback.
    Uses summarized assignment requirements to reduce token usage.
    Returns 3-5 inline feedback suggestions structured JSON feedback targeting specific areas for improvement.
    """

    # Check if assignment_id is empty to check cache
    if not input.get_assignment_id().strip():
        return "**Error:** Missing assignment ID. Please enter a valid assignment ID."

    # Check if submission is empty
    if not input.get_student_essay().strip():
        return "**Error:** No submission provided. Please enter a student submission."

    # Retrieve or make requirements summary
    requirements_submitted = get_or_store_requirements(
        input.get_assignment_id(), input.get_requirements_input()
    )

    prompt = f"""
    Instructions:
    You are an expert writing tutor providing constructive inline feedback on a student's essay.
    - Analyze the student's assignment while considering the provided **requirements**.
    - Provide **3 inline feedback points** in JSON format, ensuring feedback aligns with grading expectations.
    - EVEN IF YOU ONLY HAVE ONE, MAKE 3
    - STRICTLY RETURN ONLY JSON OUTPUT

    ### Requirements Summary:
    {requirements_submitted}

    ### Student Assignment:
    {input.get_student_essay()}

    **Format for Response (JSON Only):**
    ```json
    [
        {{"excerpt": "Some part of the student's text",
        "feedback": "Your feedback here",
        "category": "Grammar/Clarity/Argument/Structure/Requirements"}}
    ]
    ```

    **Generated Feedback (JSON Format):**
  """

    response = openai.chat.completions.create(
        model=OPEN_AI_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],  # Send entire history as messages
        temperature=TEMPERATURE,  # Increased randomness has given better results for feedback
        max_tokens=1000,
    )

    response_text = response.choices[0].message.content.strip()

    # Handle empty response
    if not response_text:
        return "No inline feedback generated. Try again."

    # Extract JSON if response contains extra text
    match = re.search(r"\[\s*{.*?}\s*\]", response_text, re.DOTALL)
    if match:
        response_text = match.group(0)

    # Attempt to parse response as JSON
    try:
        feedback_list = json.loads(response_text)
        formatted_feedback = [
            OutputFields()
            .add_student_id(input.get_student_id())
            .add_assignment_id(input.get_assignment_id())
            .add_text_snippet(item["excerpt"])
            .add_feedback(item["feedback"])
            .add_feedback_type(item["category"])
            for item in feedback_list
        ]
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        print(f"Error parsing json: ${e}")
        formatted_feedback = "--Error parsing JSON."

    return formatted_feedback


"""# Generate Summary Feedback"""


def generate_summary_feedback(input: shared.InputFields):
    """
    Generates high-level summary feedback on the entire essay, considering assignment requirements.
    Returns structured feedback on strengths, weaknesses, next steps, and rubric alignment.
    """
    # Check if assignment_id is empty to check cache
    if not input.get_assignment_id().strip():
        return "**Error:** Missing assignment ID. Please enter a valid assignment ID."

    # Check if submission is empty
    if not input.get_student_essay().strip():
        return "**Error:** No submission provided. Please enter a student submission."

    # Retrieve or make requirements summary
    requirements_submitted = get_or_store_requirements(
        input.get_assignment_id(), input.get_requirements_input()
    )

    prompt = f"""
  Instructions:
  You are an expert writing turor proing constructive inline feedback on a student essay.
  - Analyze the student's assignment while considering the provided **requirements**.
  - Provide an **overall summary of the feedback** with the following structure:
    - A brief paragraph on strengths.
    - A brief paragraph on weaknesses.
    - Two to three actionable next steps for improvements.
    - A rubric alignment score from 1 to 10.

  Format the response as:
  **Strengths:** ...
  **Weaknesses:** ...
  **Next Steps:** ...
  **Rubric Alignment:** X/10

  ### Assignment Requirements:
  {requirements_submitted}

  ### Student's Essay:
  {input.get_student_essay()}

  **Generated Summary Feedback:**
  """
    response = openai.chat.completions.create(
        model=OPEN_AI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=TEMPERATURE,  # Balance randomness for useful feedback?
        max_tokens=500,
    )

    summary_feedback = response.choices[0].message.content.strip()

    return (
        OutputFields()
        .add_student_id(input.get_student_id())
        .add_assignment_id(input.get_assignment_id())
        .add_text_snippet(input.get_student_essay())
        .add_feedback(summary_feedback)
        .add_feedback_type("Summary")
    )
