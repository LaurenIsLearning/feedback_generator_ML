from tropos.preprocess_docx import StudentSubmission
import openai
import time
from openai import RateLimitError

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

