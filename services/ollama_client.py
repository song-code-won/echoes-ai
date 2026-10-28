import requests
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, host: str = "http://127.0.0.1:11434", timeout: int = 45):
        self.host = host.rstrip("/")
        self.timeout = timeout

    def check_connection(self) -> Dict[str, Any]:
        """
        Check if Ollama service is reachable and retrieve available models.
        """
        try:
            url = f"{self.host}/api/tags"
            response = requests.get(url, timeout=4)
            if response.status_code == 200:
                data = response.json()
                models = [m.get("name") for m in data.get("models", [])]
                return {
                    "connected": True,
                    "models": models,
                    "message": f"Connected to Ollama ({len(models)} models available)."
                }
            return {
                "connected": False,
                "models": [],
                "message": f"Ollama returned HTTP status {response.status_code}."
            }
        except requests.exceptions.ConnectionError:
            return {
                "connected": False,
                "models": [],
                "message": f"Cannot connect to Ollama at {self.host}. Is Ollama running?"
            }
        except requests.exceptions.Timeout:
            return {
                "connected": False,
                "models": [],
                "message": f"Connection to Ollama timed out at {self.host}."
            }
        except Exception as e:
            return {
                "connected": False,
                "models": [],
                "message": f"Unexpected error checking Ollama: {str(e)}"
            }

    def generate(
        self,
        prompt: str,
        model: str = "qwen2.5:3b",
        system: Optional[str] = None,
        temperature: float = 0.6,
        max_tokens: int = 1500
    ) -> Dict[str, Any]:
        """
        Call Ollama generate endpoint with privacy and local security guards.
        """
        url = f"{self.host}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        if system:
            payload["system"] = system

        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "").strip()
                if not text:
                    return {
                        "success": False,
                        "text": "",
                        "error": "Model returned an empty response."
                    }
                return {
                    "success": True,
                    "text": text,
                    "error": None
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "text": "",
                    "error": f"Model '{model}' not found in local Ollama. Please run `ollama pull {model}`."
                }
            else:
                return {
                    "success": False,
                    "text": "",
                    "error": f"Ollama API returned HTTP {response.status_code}: {response.text}"
                }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "text": "",
                "error": "Ollama is not running. Please start Ollama locally (`ollama serve`)."
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "text": "",
                "error": f"Generation timed out after {self.timeout}s. The model may require more VRAM/compute."
            }
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": f"Generation failed: {str(e)}"
            }
