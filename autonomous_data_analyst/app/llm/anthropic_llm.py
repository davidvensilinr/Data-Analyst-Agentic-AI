import json
from typing import Dict, Any, Optional
import httpx
from app.llm.base_llm import BaseLLM
from config.settings import settings


class AnthropicLLM(BaseLLM):
    """Anthropic Claude LLM implementation."""
    
    def __init__(self, model: str = "claude-3-sonnet-20240229", api_key: str = None):
        self.model = model
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.base_url = "https://api.anthropic.com/v1"
        
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
    
    async def generate_response(
        self,
        prompt: str,
        max_tokens: int = 4000,
        temperature: float = 0.1,
        **kwargs
    ) -> str:
        """Generate a response from Anthropic Claude."""
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                error_text = response.text
                raise Exception(f"Anthropic API error: {response.status_code} - {error_text}")
            
            result = response.json()
            return result["content"][0]["text"]
    
    async def generate_structured_response(
        self,
        prompt: str,
        schema: Dict[str, Any],
        max_tokens: int = 4000,
        temperature: float = 0.1,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a structured response from Anthropic Claude."""
        
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
        """Estimate token count for Anthropic Claude."""
        # Anthropic uses a different tokenization, but we'll approximate
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4
    
    def estimate_cost(self, prompt: str, response: str) -> float:
        """Estimate cost of API call."""
        prompt_tokens = self.get_token_count(prompt)
        response_tokens = self.get_token_count(response)
        
        # Pricing per 1M tokens (adjust based on actual model pricing)
        if self.model == "claude-3-sonnet-20240229":
            prompt_cost_per_1m = 3.0
            response_cost_per_1m = 15.0
        elif self.model == "claude-3-haiku-20240307":
            prompt_cost_per_1m = 0.25
            response_cost_per_1m = 1.25
        else:
            # Default pricing
            prompt_cost_per_1m = 3.0
            response_cost_per_1m = 15.0
        
        prompt_cost = (prompt_tokens / 1_000_000) * prompt_cost_per_1m
        response_cost = (response_tokens / 1_000_000) * response_cost_per_1m
        
        return prompt_cost + response_cost
