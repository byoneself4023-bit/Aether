import google.generativeai as genai
from app.core.config import settings
from app.llm.base import BaseLLM


class GeminiLLM(BaseLLM):
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')

    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                ),
            )
            return response.text
        except Exception as e:
            print(f"Gemini 오류: {e}")
            return f"오류가 발생했습니다: {str(e)}"
