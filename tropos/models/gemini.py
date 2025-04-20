from tropos.preprocess_docx import StudentSubmission
import google.generativeai as genai
import time

# --------------------------
# Gemini API Caller
# --------------------------

def call_gemini(prompt: str, model_name="gemini-1.5-pro-latest", temperature=0.7, max_tokens=1500, retries=3) -> str:
    model = genai.GenerativeModel(model_name)
    
    for attempt in range(retries):
        try:
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens
                }
            )

            # SAFER extraction
            if hasattr(response, "text") and response.text:
                return response.text
            elif hasattr(response, "candidates") and response.candidates:
                return response.candidates[0].content.parts[0].text
            else:
                print("⚠️ Gemini returned no usable content.")
                return "[No feedback generated.]"

        except Exception as e:
            wait = 2 ** attempt
            print(f"⚠️ Gemini error: {e}. Retrying in {wait} seconds...")
            time.sleep(wait)
    
    raise RuntimeError("❌ Failed after multiple retries with Gemini API.")