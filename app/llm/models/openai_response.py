from dataclasses import dataclass

@dataclass
class FunctionCall:
    tool_name: str
    tool_args: str
    call_id: str

@dataclass
class OpenAIResponse:
    response: str
    function_call: FunctionCall | None = None