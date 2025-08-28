import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from backend.src.LLM.Models.IModel import IModel


class GeminiAI(IModel):
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        load_dotenv()
        api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError("Missing 'GOOGLE_GEMINI_API_KEY' environment variable")

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.prompt = None
        self.config = None
        

    def set_prompt(self, prompt: str, temperature: float = 0.5, thinking_budget: int = 512):
        self.prompt = prompt
        return
        cfg_kwargs = {}
        if temperature is not None:
            cfg_kwargs["temperature"] = temperature
        if thinking_budget is not None:
            cfg_kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=thinking_budget)
        self.config = types.GenerateContentConfig(**cfg_kwargs) if cfg_kwargs else None

    def get_text_response(self) -> str:
        if not self.prompt:
            raise ValueError("Prompt is not set. Call set_prompt() first.")

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=self.prompt,
                config=self.config
            )
            return response.text  
        except Exception as e:
            raise RuntimeError(f"Gemini API call failed: {e}")
