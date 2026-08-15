from providers.base_provider import BaseProvider
from typing import Optional, List, Dict, Any
import httpx
import json
import logging

class LocalProvider(BaseProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "llama3"):
        self.base_url = base_url
        self.model_name = model_name

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt,
            "stream": False
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=30)
                if response.status_code == 200:
                    return response.json().get("response", "")
                logging.error(f"Local Model Error: Status {response.status_code} - {response.text}")
                return f"Error: Local model failed with status {response.status_code}"
            except Exception as e:
                logging.error(f"Local Model Connection Error: {e}")
                return f"Error: Local connection failed: {str(e)}"

    async def generate_image(self, prompt: str, aspect_ratio: str = "16:9") -> str:
        # Note: Local image generation usually requires a separate endpoint like Automatic1111 or ComfyUI
        # This is a placeholder for a local Stable Diffusion API
        return "Local image generation placeholder (integrate with Stable Diffusion API here)"

    async def verify_connection(self) -> Dict[str, Any]:
        url = f"{self.base_url}/api/tags"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5)
                if response.status_code == 200:
                    return {"status": "success", "message": "Connected to Local Ollama"}
                return {"status": "error", "message": f"Local Ollama returned {response.status_code}"}
        except Exception as e:
            return {"status": "error", "message": f"Local connection failed: {str(e)}"}

    async def list_models(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/tags"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return [{"id": m["name"], "name": m["name"]} for m in data.get("models", [])]
            return []
        except:
            return []

    def get_name(self) -> str:
        return "Local (Ollama/Custom)"
