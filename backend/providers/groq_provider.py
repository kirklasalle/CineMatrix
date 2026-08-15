from typing import List, Dict, Any, Optional
from groq import AsyncGroq
from providers.base_provider import BaseProvider

class GroqProvider(BaseProvider):
    def __init__(self, api_key: str, model_name: str = "llama-3.1-70b-versatile", base_url: Optional[str] = None):
        self.client = AsyncGroq(
            api_key=api_key,
            base_url=base_url if base_url else "https://api.groq.com"
        )
        self.model_name = model_name

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages
        )
        return response.choices[0].message.content

    async def generate_image(self, prompt: str, aspect_ratio: str = "16:9") -> str:
        # Groq is focused on high-speed text inference
        raise NotImplementedError("Groq does not support image generation.")

    async def verify_connection(self) -> Dict[str, Any]:
        try:
            if not self.client.api_key:
                return {"status": "error", "message": "Groq API Key is missing"}
            await self.client.models.list()
            return {"status": "success", "message": "Connected to Groq"}
        except Exception as e:
            return {"status": "error", "message": f"Groq Error: {str(e)}"}

    async def list_models(self) -> List[Dict[str, Any]]:
        try:
            models = await self.client.models.list()
            # Groq model objects have an 'id' attribute
            return [{"id": m.id, "name": m.id} for m in models.data]
        except Exception as e:
            # Fallback to curated list if API call fails
            return [
                {"id": "llama-3.1-70b-versatile", "name": "Llama 3.1 70B Versatile"},
                {"id": "llama-3.1-8b-instant", "name": "Llama 3.1 8B Instant"},
                {"id": "mixtral-8x7b-32768", "name": "Mixtral 8x7B"}
            ]

    def get_name(self) -> str:
        return f"Groq ({self.model_name})"
