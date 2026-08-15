from typing import List, Dict, Any, Optional
from google import genai  # type: ignore
from google.genai import types  # type: ignore
from providers.base_provider import BaseProvider, ImageGenerationError  # type: ignore
import logging
import base64
import os
import uuid
import time

logger = logging.getLogger("storyboard-api")


class GoogleProvider(BaseProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = genai.Client(api_key=api_key)

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[full_prompt],
            )
            return response.text
        except Exception as e:
            logger.error(f"Google AI Generation Error: {e}")
            raise e

    async def generate_image(self, prompt: str, aspect_ratio: str = "16:9") -> dict:  # type: ignore
        """Tries multiple Google image models in sequence. Returns structured result."""
        
        # Google Nano Banana image models in order of preference
        models_to_try = [
            ("gemini-3.1-flash-image-preview", "Nano Banana 2 Preview"),
            ("gemini-3-pro-image-preview", "Nano Banana Pro Preview"),
            ("gemini-2.5-flash-preview-image-generation", "Nano Banana"),
            ("imagen-3.0-generate-002", "Imagen 3"),
            ("imagen-3.0-fast-generate-001", "Imagen 3 Fast"),
        ]
        
        attempts: List[Dict[str, Any]] = []
        
        for model_id, display_name in models_to_try:
            try:
                logger.info(f"Google: Trying image model {display_name} ({model_id})")
                
                if model_id.startswith("imagen"):
                    # Imagen uses a dedicated image generation endpoint
                    result = self._generate_with_imagen(model_id, prompt)
                else:
                    # Nano Banana models use generate_content with response_modalities
                    result = self._generate_with_gemini_image(model_id, prompt)
                
                if result:
                    attempts.append({"model": display_name, "status": "success"})
                    return {
                        "image_url": result,
                        "model_used": display_name,
                        "provider": "Google AI",
                        "attempts": attempts
                    }
                else:
                    attempts.append({
                        "model": display_name, 
                        "status": "failed",
                        "reason": "Model returned no image data"
                    })
                    
            except Exception as e:
                error_str = str(e)
                if "not found" in error_str.lower():
                    reason = f"{display_name} not available in your region/tier"
                elif "403" in error_str or "permission" in error_str.lower():
                    reason = f"Access denied for {display_name}"
                elif "safety" in error_str.lower() or "blocked" in error_str.lower():
                    reason = f"Content filtered by {display_name}"
                else:
                    reason = error_str[:120]  # type: ignore
                
                attempts.append({"model": display_name, "status": "failed", "reason": reason})
                logger.warning(f"Google: {display_name} failed: {reason}")
                continue
        
        # All models failed
        raise ImageGenerationError("No Google image models available", attempts)

    def _generate_with_gemini_image(self, model_id: str, prompt: str) -> Optional[str]:
        """Generate image using Gemini Nano Banana models (generate_content with image output)."""
        response = self.client.models.generate_content(
            model=model_id,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )
        
        # Extract image from response parts
        for part in response.candidates[0].content.parts:  # type: ignore
            if part.inline_data is not None:
                # Convert binary image data to a data URL for the frontend
                mime_type = part.inline_data.mime_type or "image/png"
                image_bytes = part.inline_data.data
                b64 = base64.b64encode(image_bytes).decode("utf-8")
                return f"data:{mime_type};base64,{b64}"
        
        return None

    def _generate_with_imagen(self, model_id: str, prompt: str) -> Optional[str]:
        """Generate image using Imagen models."""
        try:
            response = self.client.models.generate_images(  # type: ignore
                model=model_id,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                ),
            )
            
            if response.generated_images:  # type: ignore
                image = response.generated_images[0]  # type: ignore
                image_bytes = image.image.image_bytes  # type: ignore
                b64 = base64.b64encode(image_bytes).decode("utf-8")
                return f"data:image/png;base64,{b64}"
        except Exception:
            raise
        
        return None

    async def verify_connection(self) -> Dict[str, Any]:
        try:
            # Quick test with a simple generation
            self.client.models.list()
            return {"status": "success", "message": "Connected to Google AI"}
        except Exception as e:
            return {"status": "error", "message": f"Google AI Error: {str(e)}"}

    async def list_models(self) -> List[Dict[str, Any]]:
        try:
            models_list = []
            for model in self.client.models.list():
                model_id = model.name if hasattr(model, 'name') else str(model)  # type: ignore
                display = model.display_name if hasattr(model, 'display_name') else model_id  # type: ignore
                models_list.append({"id": model_id, "name": display})
            # Sort so Gemini models appear first
            models_list.sort(key=lambda x: ("gemini" not in x["id"].lower(), x["id"]))
            return models_list
        except Exception as e:
            logger.error(f"Google: Failed to list models: {e}")
            return [
                {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash"},
                {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro"},
            ]

    def get_name(self) -> str:
        return f"Google ({self.model_name})"


class ImageGenerationError(Exception):
    """Custom exception that carries the attempt log."""
    def __init__(self, message: str, attempts: list):
        super().__init__(message)
        self.attempts = attempts
