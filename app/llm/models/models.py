from dataclasses import dataclass
from typing import Union
from enum import Enum

@dataclass
class TextContent:
    text: str

@dataclass
class FileContent:
    file_name: str
    file_data: str

Content = Union[
    TextContent,
    FileContent
]

class ContextItem:
    pass

@dataclass
class ContextRoleItem(ContextItem):
    role: str
    content: list[Content]

@dataclass
class ContextToolOutputItem(ContextItem):
    tool_call_id: str
    tool_output: str