import os
import re
import json
from dotenv import load_dotenv
from openai import OpenAI
from src.LLM.Models.IModel import IModel


class ChatGPTAI(IModel):
    def __init__(self, model_name: str = "gpt-4.1"):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("Missing 'OPENAI_API_KEY' environment variable")

        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        self.prompt = None
        self.temperature = 0.5

    def set_prompt(self, prompt: str, temperature: float = 0.5):
        self.prompt = prompt
        if temperature is not None:
            self.temperature = temperature

    def get_text_response(self) -> str:
        if not self.prompt:
            raise ValueError("Prompt is not set. Call set_prompt() first.")

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": self.prompt}],
                temperature=self.temperature,
            )
            text = response.choices[0].message.content.strip()
            if not text:
                raise RuntimeError("ChatGPT returned an empty response.")

            print("ChatGPT raw text:", repr(text[:300]))
            return text
        except Exception as e:
            raise RuntimeError(f"ChatGPT API call failed: {e}")

    def get_json_response(self) -> dict:
        try:
            return json.loads(self.get_text_response())
        except json.JSONDecodeError:
            print("ChatGPT returned non-JSON text, wrapping into fallback:")
            return {"raw_text": ""}
