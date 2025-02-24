import google.generativeai as genai
from config.settings import settings

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            "gemini-2.0-flash",
            generation_config={"response_mime_type": "application/json"}
        )

    async def analyze(self, prompt: str, data: str = None) -> str:
        full_prompt = f"{prompt}\n\nData:\n{data[:15000]}" if data else prompt
        response = self.model.generate_content(full_prompt)
        return response.text
