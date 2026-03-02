import json
import tiktoken
from typing import Dict, Any, Optional
import httpx
from app.llm.base_llm import BaseLLM
from config.settings import settings


class OpenAILLM(BaseLLM):
    """OpenAI GPT LLM implementation."""
    
    def __init__(self, model: str = "gpt-3.5-turbo", api_key: str = None):
        self.model = model
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1"
        self.encoding = tiktoken.encoding_for_model(model)
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
    
    async def generate_response(
        self,
        prompt: str,
        max_tokens: int = 4000,
        temperature: float = 0.1,
        **kwargs
    ) -> str:
        """Generate a response from OpenAI GPT."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert data analyst assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                error_text = response.text
                raise Exception(f"OpenAI API error: {response.status_code} - {error_text}")
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    async def generate_structured_response(
        self,
        prompt: str,
        schema: Dict[str, Any],
        max_tokens: int = 4000,
        temperature: float = 0.1,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a structured response from OpenAI GPT."""
        
        # Add schema instructions to prompt
        schema_instruction = f"""
Please respond with a valid JSON object that follows this schema:
{json.dumps(schema, indent=2)}

Your response must be valid JSON only, no additional text."""
        
        full_prompt = f"{prompt}\\n\\n{schema_instruction}"
        
        response_text = await self.generate_response(
            prompt=full_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        
        try:
            # Parse JSON response
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\\{.*\\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise ValueError(f"Failed to parse JSON response: {response_text}")
    
    def get_token_count(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        return len(self.encoding.encode(text))
    
    def estimate_cost(self, prompt: str, response: str) -> float:
        """Estimate cost of API call."""
        prompt_tokens = self.get_token_count(prompt)
        response_tokens = self.get_token_count(response)
        
        # Pricing per 1K tokens (adjust based on actual model pricing)
        if self.model == "gpt-3.5-turbo":
            prompt_cost_per_1k = 0.0015
            response_cost_per_1k = 0.002
        elif self.model == "gpt-4":
            prompt_cost_per_1k = 0.03
            response_cost_per_1k = 0.06
        else:
            # Default pricing
            prompt_cost_per_1k = 0.0015
            response_cost_per_1k = 0.002
        
        prompt_cost = (prompt_tokens / 1000) * prompt_cost_per_1k
        response_cost = (response_tokens / 1000) * response_cost_per_1k
        
        return prompt_cost + response_cost
