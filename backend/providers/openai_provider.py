from providers.base_provider import BaseProvider, ImageGenerationError  # type: ignore
from typing import Optional, List, Dict, Any
import openai  # type: ignore
import os


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str, base_url: Optional[str] = None, model_name: Optional[str] = None):
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=base_url if base_url else "https://api.openai.com/v1"
        )
        self.model_name = model_name or "gpt-4o"

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

    async def generate_image(self, prompt: str, aspect_ratio: str = "16:9") -> dict:  # type: ignore
        """Returns a dict with image_url, model_used, and attempts log."""
        size_map = {
            "16:9": "1792x1024",
            "9:16": "1024x1792",
            "1:1": "1024x1024"
        }
        size = size_map.get(aspect_ratio, "1024x1024")
        
        models_to_try = ["gpt-image-1", "dall-e-3", "dall-e-2"]
        attempts: List[Dict[str, Any]] = []
        
        for model in models_to_try:
            try:
                current_size = "1024x1024" if model == "dall-e-2" else size
                response = await self.client.images.generate(
                    model=model,
                    prompt=prompt,
                    size=current_size,
                    quality="standard",
                    n=1,
                )
                attempts.append({"model": model, "status": "success"})
                return {
                    "image_url": response.data[0].url,  # type: ignore
                    "model_used": model,
                    "provider": "OpenAI",
                    "attempts": attempts
                }
            except Exception as e:
                error_str = str(e)
                if "does not have access" in error_str:
                    reason = f"Project does not have access to {model}"
                elif "403" in error_str:
                    reason = f"Access denied for {model}"
                elif "model_not_found" in error_str:
                    reason = f"{model} not available"
                else:
                    reason = error_str[:120]  # type: ignore
                
                attempts.append({"model": model, "status": "failed", "reason": reason})
                
                if "403" in error_str or "model_not_found" in error_str or "does not have access" in error_str:
                    continue
                else:
                    raise
        
        raise ImageGenerationError("No OpenAI image models available", attempts)

    async def verify_connection(self) -> Dict[str, Any]:
        try:
            await self.client.models.list()
            return {"status": "success", "message": "Connected to OpenAI"}
        except Exception as e:
            return {"status": "error", "message": f"OpenAI Error: {str(e)}"}

    async def list_models(self) -> List[Dict[str, Any]]:
        try:
            models = await self.client.models.list()
            all_models = [{"id": m.id, "name": m.id} for m in models.data]
            all_models.sort(key=lambda x: ("gpt" not in x["id"], x["id"]))
            return all_models
        except:
            return [{"id": "gpt-4o", "name": "gpt-4o"}, {"id": "gpt-4-turbo", "name": "gpt-4-turbo"}]

    def get_name(self) -> str:
        return "OpenAI"
