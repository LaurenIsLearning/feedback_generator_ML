import os
import time
import anthropic
from anthropic import RateLimitError

# Initialize the Anthropic client using the API key from environment variable
client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

def call_claude(
    prompt: str,
    model: str = "claude-3-opus-20240229",
    temperature: float = 0.7,
    max_tokens: int = 1500,
    retries: int = 3
) -> str:
    for attempt in range(retries):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system="You are a college writing professor providing detailed feedback.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except RateLimitError:
            wait = 2 ** attempt
            print(f"⚠️ Claude rate limit hit. Waiting {wait:.1f} seconds before retrying...")
            time.sleep(wait)

    raise RuntimeError("❌ Claude API failed after multiple retries.")
