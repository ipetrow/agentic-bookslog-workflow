from dataclasses import dataclass

@dataclass
class ToolUse:
    tool_name: str
    tool_args: str
    call_id: str

@dataclass
class LLMResponse:
    response: str | None = None
    tool_use: ToolUse | None = None

    @property
    def is_final(self) -> bool:
        return self.tool_use is None