import os
import requests
import json
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OllamaManager:
    def __init__(self):
        self.host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3:8b")
        self.math_model = os.getenv("OLLAMA_MATH_MODEL", "qwen2.5-math:7b")
        self._check_connection()

    def _check_connection(self):
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info(f"Connected to Ollama at {self.host}")
            else:
                logger.warning(f"Ollama responded with status {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            logger.warning("Ollama may not be running. Start it with: docker-compose up -d ollama")

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        try:
            model_name = model or self.model
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            raise

    def generate_structured(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        try:
            model_name = model or self.model
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": temperature
                    }
                },
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            response_text = result.get("response", "")
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Failed to generate structured response: {e}")
            raise

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        try:
            model_name = model or self.model
            response = requests.post(
                f"{self.host}/api/chat",
                json={
                    "model": model_name,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature
                    }
                },
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            return result.get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"Failed to chat: {e}")
            raise

    def list_models(self) -> List[str]:
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            response.raise_for_status()
            result = response.json()
            models = result.get("models", [])
            return [model.get("name", "") for model in models]
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    def pull_model(self, model_name: str):
        try:
            logger.info(f"Pulling model {model_name}...")
            response = requests.post(
                f"{self.host}/api/pull",
                json={"name": model_name, "stream": True},
                timeout=600
            )
            response.raise_for_status()
            logger.info(f"Successfully pulled model {model_name}")
        except Exception as e:
            logger.error(f"Failed to pull model: {e}")
            raise
