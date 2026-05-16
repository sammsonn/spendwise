from google import genai
from django.conf import settings

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def generate(prompt: str) -> str:
    response = _get_client().models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=prompt,
    )
    return response.text
