from typing import List, Dict, Any, Optional
import anthropic
from providers.base_provider import BaseProvider

class AnthropicProvider(BaseProvider):
    def __init__(self, api_key: str, model_name: str = "claude-3-5-sonnet-20240620", base_url: Optional[str] = None):
        self.client = anthropic.AsyncAnthropic(
            api_key=api_key,
            base_url=base_url if base_url else "https://api.anthropic.com"
        )
        self.model_name = model_name

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = [{"role": "user", "content": prompt}]
        response = await self.client.messages.create(
            model=self.model_name,
            max_tokens=2000,
            system=system_prompt if system_prompt else "",
            messages=messages
        )
        return response.content[0].text

    async def generate_image(self, prompt: str, aspect_ratio: str = "16:9") -> str:
        # Anthropic doesn't have image generation yet, so we'll return a placeholder or error
        # In a real app, we might fall back to another provider or just inform the user
        raise NotImplementedError("Anthropic does not support native image generation yet.")

    async def verify_connection(self) -> Dict[str, Any]:
        try:
            if not self.client.api_key:
                return {"status": "error", "message": "Anthropic API Key is missing"}
            await self.client.messages.create(
                model=self.model_name or "claude-3-5-haiku-latest",
                max_tokens=1,
                messages=[{"role": "user", "content": "ping"}]
            )
            return {"status": "success", "message": "Connected to Anthropic"}
        except anthropic.AuthenticationError as e:
            return {"status": "error", "message": f"Anthropic Authentication Error: Invalid API key"}
        except Exception as e:
            return {"status": "error", "message": f"Anthropic Error: {str(e)}"}

    async def list_models(self) -> List[Dict[str, Any]]:
        # Anthropic doesn't have a public models list API that's easily accessible via the SDK yet
        # Returning a curated list of their latest models
        return [
            {"id": "claude-3-5-sonnet-latest", "name": "Claude 3.5 Sonnet (Latest)"},
            {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet (2024-10-22)"},
            {"id": "claude-3-5-sonnet-20240620", "name": "Claude 3.5 Sonnet (2024-06-20)"},
            {"id": "claude-3-5-haiku-latest", "name": "Claude 3.5 Haiku (Latest)"},
            {"id": "claude-3-opus-latest", "name": "Claude 3 Opus (Latest)"},
            {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet (2024-02-29)"},
            {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku (2024-03-07)"}
        ]

    def get_name(self) -> str:
        return f"Anthropic ({self.model_name})"
