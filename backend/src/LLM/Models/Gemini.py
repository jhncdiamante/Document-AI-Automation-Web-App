import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from src.LLM.Models.IModel import IModel
import json

import re, json
def safe_json_parse(text: str):
    # Strip triple quotes and markdown fences
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()


    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        # Fallback: try to extract first {...} block
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                block = match.group()
                block = re.sub(r'(\d+)\s*%', r'"\1%"', block)
                return json.loads(block)
            except:
                pass
        raise RuntimeError(f"Gemini returned non-JSON text: {text}") from e



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
            if not response.text or not response.text.strip():
                raise RuntimeError("Gemini returned an empty response.")

            print("Gemini raw text:", repr(response.text[:300]))
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API call failed: {e}")

    def get_json_response(self) -> dict:
        raw_text = self.get_text_response()
        try:
            return safe_json_parse(raw_text)

        except json.JSONDecodeError:
            print("Gemini returned non-JSON text, wrapping into fallback:")
            return {"raw_text": raw_text}
