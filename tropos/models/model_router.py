# Routes prompt calls to GPT or Gemini ect
from tropos.preprocess_docx import StudentSubmission
from tropos.models import gpt, gemini

# set up for default to be gpt-4o unless otherwise stated
# TODO: come back and add variants of GPT and other models
def call_model(prompt: str, model_name: str = "gpt-4o"):
    if model_name == "gpt-4o":
        return gpt.call_chatgpt(prompt)
    elif model_name == "gemini-2.5-pro-exp-03-25":
        return gemini.call_gemini(prompt)
    else:
        raise ValueError(f"Unsupported model: {model_name}")