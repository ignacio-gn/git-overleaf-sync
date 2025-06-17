import json
import logging
from datetime import datetime

import requests

OLLAMA_MODEL= "llama3.3:latest"

logger = logging.getLogger(__name__)

def get_hour():
    return datetime.now().strftime("%Y-%m-%d-%H")


class OpenWebUIHelper:
    def __init__(self, openwebui_url: str, api_key: str, model: str = OLLAMA_MODEL):
        self.openwebui_url = openwebui_url
        self.api_key = api_key

    def chat_with_model(self, prompt: str):
        url = f'{self.openwebui_url}/api/chat/completions'
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            "model": "llama3.3:latest",
            "messages": [
                {
                    "role": "user",
                    "content": prompt + \
                    f"Generate a concise (50-80 characters) commit message for the above changes." \
                    f"The message should be in the imperative mood and briefly describe the changes made." \
                    f"Only return the commit message, no other text."
                }
            ]
        }
        response = requests.post(url, headers=headers, json=data)
        response_str = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response from model.")
        return response_str
