from abc import ABC, abstractmethod

from .models.models import ContextItem

class LLMService(ABC):

    @abstractmethod
    async def process(self, context_item: ContextItem, available_tools: list = None) -> str:
        pass