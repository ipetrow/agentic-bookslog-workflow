from dataclasses import dataclass
from enum import Enum

class ItemType(Enum):
    TOOL = "tool"
    RESOURCE = "resource"

@dataclass(frozen=True)
class ItemKey:
    type: ItemType
    name: str

@dataclass
class ToolCallResponse:
    content: str
    log: str