from config.settings import settings
from collections import defaultdict

class GeminiService:
    def __init__(self):
        try:
            import google.generativeai as genai
            if not settings.GEMINI_API_KEY:
                raise ValueError("Missing GEMINI_API_KEY in settings")
            genai.configure(api_key=settings.GEMINI_API_KEY)
        except ImportError:
            raise Exception("Failed to import Google GenerativeAI library. Run: pip install google-generativeai")
        
        self.model = genai.GenerativeModel(
            "gemini-2.0-flash",
            generation_config={"response_mime_type": "application/json"}
        )

    async def analyze(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        try:
            if kwargs:
                kwargs = defaultdict(str, kwargs)
                prompt = prompt.format_map(kwargs)
            
            # Create a conversation with system prompt if provided
            if system_prompt:
                response = self.model.generate_content(
                    [
                        {"role": "system", "parts": [system_prompt]},
                        {"role": "user", "parts": [prompt]}
                    ]
                )
            else:
                response = self.model.generate_content(prompt)
                
            if hasattr(response, 'text'):
                return response.text
            else:
                return str(response)
                
        except Exception as e:
            import traceback
            return f"Error analyzing prompt: {str(e)} \n{traceback.format_exc()}"
        
class ChatGPTService:
    def __init__(self):
        try: 
            import openai
            if not settings.OPENAI_API_KEY:
                raise ValueError("Missing OPENAI_API_KEY in settings")
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        except ImportError:
            raise Exception("Failed to import OpenAI library. Run: pip install openai")
        
        self.model = "gpt-3.5-turbo"

    async def analyze(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        try:
            if kwargs:
                kwargs = defaultdict(str, kwargs)
                prompt = prompt.format_map(kwargs)

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1000)   
            )

            return response.choices[0].message.content
        except Exception as e:
            import traceback
            return f"Error analyzing prompt: {str(e)} \n{traceback.format_exc()}"
