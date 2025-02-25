import google.generativeai as genai
from config.settings import settings
from collections import defaultdict

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            "gemini-2.0-flash",
            generation_config={"response_mime_type": "application/json"}
        )

    async def analyze(self, prompt: str, **kwargs) -> str:
        try:
            if kwargs:
                kwargs = defaultdict(str, kwargs)
                prompt = prompt.format_map(kwargs)
            response = self.model.generate_content(prompt)
            if hasattr(response, 'text'):
                return response.text
            else:
                return str(response)
                
        except Exception as e:
            return f"Error analyzing prompt: {str(e)}"
