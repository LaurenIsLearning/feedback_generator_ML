from tropos.preprocess_docx import StudentSubmission
from openai import OpenAI
import time
import os
from google.colab import userdata
deepseek_key = userdata.get("deepseek").strip()

class DeepSeekClient:
    def __init__(self):
        self.base_url = "https://api.deepseek.com/v1"
        self.client = OpenAI(
            api_key=deepseek_key,
            base_url=self.base_url
        )

    def chat_completion(self, prompt, model="deepseek-chat", **kwargs):
        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    **kwargs
                )
                return response.choices[0].message.content
            except Exception as e:
                wait = 2 ** attempt
                print(f"⚠️ Rate limit hit. Waiting {wait} seconds before retrying...")
                time.sleep(wait)
        raise RuntimeError("API request failed after 3 attempts")

_deepseek_client = DeepSeekClient()

def call_deepseek(prompt, model_name="deepseek-chat", **kwargs):
    return _deepseek_client.chat_completion(prompt, model=model_name, **kwargs)