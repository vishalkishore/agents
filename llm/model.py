import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv() 

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


genai.configure(api_key=GEMINI_API_KEY)

gemini = genai.GenerativeModel('gemini-2.0-flash',generation_config={
    'response_mime_type': 'application/json',
}) if GEMINI_API_KEY else None