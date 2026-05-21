import json

from app.llm.models.models import (
    ContextRoleItem, TextContent, FileContent, ContextToolOutputItem
)

class OpenAIContextMapper:

    async def _serialize_content_items(self, content_items: list) -> list:

        serialized_content_items = []
        for content_item in content_items:
            if isinstance(content_item, TextContent):
                serialized_content_items.append({
                    "type": "input_text",
                    "text": content_item.text
                })
            elif isinstance(content_item, FileContent):
                serialized_content_items.append({
                    "type": "input_file",
                    "filename": content_item.file_name,
                    "file_data": f"data:application/pdf;base64,{content_item.file_base64}",
                })

        return serialized_content_items

    async def serialize_context_role_item(self, context_item: ContextRoleItem):

        # TODO exception in case the instance is not ContextRoleItem

        serialized_content_items = await self._serialize_content_items(context_item.content)

        serialized_context_item = {
            "role": context_item.role,
            "content": serialized_content_items
        }

        return serialized_context_item

    async def serialize_context_tool_output_item(self, context_item: ContextToolOutputItem) -> str:

        # TODO exception in case the instance is not ContextToolOutputItem

        serialized_context_item = {
            "type": "function_call_output",
            "call_id": context_item.tool_call_id,
            "output": context_item.tool_output
        }

        return json.dumps(serialized_context_item)
    
    async def serialize_tools(self, available_tools: list) -> list:
        serialized_tools = [
            {
                "type": "function",
                "name": tool.name,
                "description": tool.description,
                "parameters": getattr(
                        tool,
                        "inputSchema",
                        {"type": "object", "properties": {}}
                    )
            }
            for tool in available_tools.tools
        ]

        return serialized_tools