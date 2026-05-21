
from dataclasses import dataclass

@dataclass
class Tool:
    name: str
    args: str

@dataclass
class OpenAIResponse:
    response: str
    function_call: Tool | None = None