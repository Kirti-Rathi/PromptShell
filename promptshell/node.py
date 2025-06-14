import requests
import json
from openai import OpenAI
import anthropic
import google.generativeai as genai
from groq import Groq
from tqdm import tqdm
from .setup import get_provider
from typing import List, Tuple

class Node:
    def __init__(self, model_name: str, name: str, max_tokens: int = 8192, config: dict = None):
        self.model_name = model_name
        self.name = name
        self.definition = ""
        self.context = []
        self.max_tokens = max_tokens
        self.config = config or {}
        self.provider = get_provider()

    def __call__(self, input_text: str, additional_data: dict = None):
        try:
            context_str = "\n".join([f"{msg['role']} {msg['content']}" for msg in self.context])
            prompt = f""" system {self.definition} 
{context_str}
 user {input_text} """
            if additional_data:
                prompt += "\n system Additional data:\n"
                for key, value in additional_data.items():
                    prompt += f"{key}: {value}\n"
                prompt += " "
            prompt += "\n assistant "

            with tqdm(total=1, desc=f"{self.name} Processing", bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}') as pbar:
                if self.provider == "ollama":
                    response = self._call_ollama(prompt)
                elif self.provider == "openai":
                    response = self._call_openai(prompt)
                elif self.provider == "anthropic":
                    response = self._call_anthropic(prompt)
                elif self.provider == "google":
                    response = self._call_google(prompt)
                elif self.provider == "groq":
                    response = self._call_groq(prompt)
                elif self.provider == "fireworks":
                    response = self._call_fireworks(prompt)
                elif self.provider == "openrouter":
                    response = self._call_openrouter(prompt)
                elif self.provider == "deepseek":
                    response = self._call_deepseek(prompt)
                else:
                    return "Unsupported provider."
                pbar.update(1)

            output = response.strip()
            self.context.append({"role": "user", "content": input_text})
            self.context.append({"role": "assistant", "content": output})
            return output

        except Exception as e:
            return f"Error in processing: {str(e)}"

    def _call_ollama(self, prompt: str) -> str:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "stop": [" ", " ", " "],
                    "num_predict": self.max_tokens
                }
            }
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            return f"Error in Ollama API call: {response.status_code} - {response.text}"


    def _call_openai(self, prompt: str) -> str:
        api_key = self.config["OPENAI_API_KEY"]
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    def _call_anthropic(self, prompt: str) -> str:
        api_key = self.config["ANTHROPIC_API_KEY"]
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=self.model_name,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

    def _call_google(self, prompt: str) -> str:
        api_key = self.config["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(self.model_name)
        response = model.generate_content(prompt)
        return response.text.strip()

    def _call_groq(self, prompt: str) -> str:
        api_key = self.config["GROQ_API_KEY"]
        client = Groq(api_key=api_key)
        
        messages = [
            {
                "role": "system",
                "content": "Always respond in valid JSON format using double quotes with a 'command' key."
            },
            {
                "role": "user", 
                "content": f"{prompt}. Return ONLY a JSON object with a 'command' key."
            }
        ]
        
        response = client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"},
        )
        
        # Extract and parse the JSON response
        response_json = json.loads(response.choices[0].message.content.strip())
        return response_json["command"].strip()
    
    def _call_fireworks(self, prompt: str) -> str:
        """Handle API calls for Fireworks AI provider"""
        api_key = self.config["FIREWORKS_API_KEY"]
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.fireworks.ai/inference/v1/accounts/fireworks/models/",
        )
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content.strip()
    
    def _call_openrouter(self, prompt: str) -> str:
        """Handle API calls for OpenRouter provider"""
        api_key = self.config["OPENROUTER_API_KEY"]
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": self.config.get("OPENROUTER_REFERER", "https://github.com/your-repo"),
                "X-Title": self.config.get("OPENROUTER_TITLE", "AI Application"),
            }
        )
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content.strip()
    
    def _call_deepseek(self, prompt: str) -> str:
        """Handle API calls for DeepSeek provider"""
        api_key = self.config["DEEPSEEK_API_KEY"]
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1",
        )
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_tokens,
            temperature=0.3  # Recommended default for DeepSeek
        )
        return response.choices[0].message.content.strip()

