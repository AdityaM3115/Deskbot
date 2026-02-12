import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

client = genai.Client(api_key=api_key)


def ask_gemini(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        if response and response.text:
            return response.text.strip()

        return "I could not generate a response."

    except Exception as e:
        print(f"[ERROR] Gemini request failed: {e}")
        return "There was an error contacting the AI service."