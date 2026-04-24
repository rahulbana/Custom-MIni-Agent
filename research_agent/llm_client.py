import openai
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger
from .config import config

class LLMClient:
    def __init__(self, api_key: str = None):
        self.client = openai.AsyncOpenAI(api_key=api_key or config.openai_api_key)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat.completions.create(
            model=config.openai_model,
            messages=messages,
            temperature=config.temperature,
            timeout=config.request_timeout
        )
        return response.choices[0].message.content
