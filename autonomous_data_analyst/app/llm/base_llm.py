from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseLLM(ABC):
    """Base class for LLM implementations."""
    
    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        max_tokens: int = 4000,
        temperature: float = 0.1,
        **kwargs
    ) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    async def generate_structured_response(
        self,
        prompt: str,
        schema: Dict[str, Any],
        max_tokens: int = 4000,
        temperature: float = 0.1,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a structured response from the LLM."""
        pass
    
    @abstractmethod
    def get_token_count(self, text: str) -> int:
        """Count tokens in text."""
        pass
    
    @abstractmethod
    def estimate_cost(self, prompt: str, response: str) -> float:
        """Estimate cost of API call."""
        pass
