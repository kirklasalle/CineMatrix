from typing import List, Dict, Any, Optional
import time
import logging
import httpx
from openai import AsyncOpenAI
from providers.base_provider import BaseProvider

class OpenRouterProvider(BaseProvider):
    def __init__(self, api_key: str, model_name: str = "meta-llama/llama-3.1-8b-instruct:free", base_url: Optional[str] = None):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url or "https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/kirklasalle/storyboard",
                "X-Title": "Storyboard AI",
            }
        )
        self.model_name = model_name

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            if "402" in error_msg:
                logging.error(f"OpenRouter: Insufficient credits or token limit reached. Details: {error_msg}")
                raise Exception("OpenRouter: Insufficient Credits. Please top up your account at openrouter.ai.")
            logging.error(f"OpenRouter Generation Error: {e}")
            raise e

    async def generate_image(self, prompt: str, aspect_ratio: str = "16:9") -> str:
        # OpenRouter doesn't have a standardized image generation endpoint yet
        raise NotImplementedError("OpenRouter does not support native image generation yet.")

    async def verify_connection(self) -> Dict[str, Any]:
        if not self.client.api_key:
            return {"status": "error", "message": "OpenRouter API Key is missing. Please enter your API Key."}
        start_time = time.time()
        logging.info(f"OpenRouter: Verifying connection...")
        try:
            headers = {"Authorization": f"Bearer {self.client.api_key}"}
            async with httpx.AsyncClient() as client:
                response = await client.get("https://openrouter.ai/api/v1/auth/key", headers=headers, timeout=5)
                duration = time.time() - start_time
                logging.info(f"OpenRouter: Connection verification status={response.status_code} duration={duration:.2f}s")
                
                if response.status_code == 200:
                    return {"status": "success", "message": "Connection successful"}
                elif response.status_code == 401:
                    return {"status": "error", "message": "Unauthorized: Please check your OpenRouter API Key."}
                else:
                    try:
                        detail = response.json().get('error', {}).get('message', response.text)
                    except:
                        detail = response.text
                    return {"status": "error", "message": f"OpenRouter Error {response.status_code}: {detail}"}
        except Exception as e:
            logging.error(f"OpenRouter: Connection verification failed: {e}")
            return {"status": "error", "message": f"Connection Exception: {str(e)}"}

    _models_cache = []
    _last_fetch = 0
    CACHE_DURATION = 300 # 5 minutes

    async def list_models(self) -> List[Dict[str, Any]]:
        # Check cache
        if self._models_cache and (time.time() - self._last_fetch < self.CACHE_DURATION):
            logging.info("OpenRouter: Returning cached models list")
            return self._models_cache

        start_time = time.time()
        logging.info(f"OpenRouter: Fetching models list via direct API...")
        try:
            # Use direct httpx to avoid OpenAI SDK overhead for large model lists
            headers = {
                "HTTP-Referer": "https://github.com/kirklasalle/storyboard",
                "X-Title": "Storyboard AI"
            }
            if self.client.api_key:
                headers["Authorization"] = f"Bearer {self.client.api_key}"
            async with httpx.AsyncClient() as client:
                response = await client.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json().get('data', [])
                    duration = time.time() - start_time
                    logging.info(f"OpenRouter: Model list fetched count={len(data)} duration={duration:.2f}s")
                    
                    # Return the full list of models
                    curated = [{"id": m['id'], "name": m.get('name', m['id'])} for m in data]
                    
                    # Update class-level cache
                    OpenRouterProvider._models_cache = curated
                    OpenRouterProvider._last_fetch = time.time()
                    return curated
                else:
                    logging.error(f"OpenRouter: Models API returned {response.status_code}")
                    return [{"id": "meta-llama/llama-3.1-8b-instruct:free", "name": "Llama 3.1 8B (Free)"}]
        except Exception as e:
            logging.error(f"OpenRouter: Model List Error: {e}")
            return [{"id": "meta-llama/llama-3.1-8b-instruct:free", "name": "Llama 3.1 8B (Free)"}]

    async def get_balance(self) -> Dict[str, Any]:
        if not self.client.api_key:
            return {"status": "error", "message": "OpenRouter API Key is missing."}
        logging.info("OpenRouter: Fetching account balance...")
        headers = {"Authorization": f"Bearer {self.client.api_key}"}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get("https://openrouter.ai/api/v1/credits", headers=headers, timeout=5)
                if response.status_code == 200:
                    data = response.json().get('data', {})
                    total_credits = data.get('total_credits', 0)
                    total_usage = data.get('total_usage', 0)
                    balance = total_credits - total_usage
                    return {
                        "status": "success",
                        "credits": round(total_credits, 4),
                        "usage": round(total_usage, 4),
                        "balance": round(balance, 4),
                        "currency": "USD"
                    }
                else:
                    return {"status": "error", "message": f"API returned {response.status_code}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

    def get_name(self) -> str:
        return f"OpenRouter ({self.model_name})"
