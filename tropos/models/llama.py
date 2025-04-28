from tropos.preprocess_docx import StudentSubmission
from openai import OpenAI
import os

class LlamaClient:
    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("LLAMA_API_URL"),
            api_key=os.getenv("LLAMA_API_KEY")
        )

    def chat_completion(self, prompt, model_name="meta-llama/llama-4-scout-17b-16e-instruct", **kwargs):
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a college writing professor."},
                {"role": "user", "content": prompt}
            ],
            **kwargs
        )
        return response.choices[0].message.content

_llama_client = LlamaClient()

def call_llama(prompt,
              model_name="meta-llama/llama-4-scout-17b-16e-instruct",
               **kwargs):
    return _llama_client.chat_completion(prompt, model_name, **kwargs)