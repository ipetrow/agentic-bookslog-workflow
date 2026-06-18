import json

from .models.models import (
    ContextRoleItem, TextContent, FileContent, ContextToolOutputItem
)

class AnthropicContextMapper:
    """
    A mapper converting context history items to the format compatible with Anthropic Claude Messages API.
    """

    async def _serialize_content_items(self, content_items: list) -> list:
        """
        Maps the context's content items to to the format compatible with OpenAI Responses API.
        
        Args:
            content_items: The context's content items for mapping.

        Returns:
            A list of mapped content items compatible with the OpenAI Responses API.
        """

        serialized_content_items = []
        for content_item in content_items:
            if isinstance(content_item, TextContent):
                serialized_content_items.append({
                    "type": "text",
                    "text": content_item.text
                })
            elif isinstance(content_item, FileContent):
                serialized_content_items.append({
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": f"{content_item.file_data}"
                    }
                })

        return serialized_content_items

    async def serialize_context_role_item(self, context_item: ContextRoleItem) -> dict:
        """
        Maps a context item with a role attribute to a format compatible with the Anthropic Claude Message API.

        Args:
            context_item: The context item for mapping.

        Returns:
            A dictionary in the format compatible with the Anthropic Claude Message API.
        """

        serialized_content_items = await self._serialize_content_items(context_item.content)

        serialized_context_item = {
            "role": context_item.role,
            "content": serialized_content_items
        }

        return serialized_context_item

    async def serialize_context_tool_output_item(self, context_item: ContextToolOutputItem) -> dict:
        """
        Maps a context item with a tool ouput to a format compatible with the Anthropic Claude Message API.

        Args:
            context_item: The context item for mapping.

        Returns:
            A dictionary in the format compatible with the Anthropic Claude Message API.
        """

        serialized_context_item = {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": context_item.tool_call_id,
                    "content": context_item.tool_output
                }
            ]
        }

        return serialized_context_item
    
    async def serialize_tools(self, available_tools: list) -> list:
        """
        Maps the tools to a format compatible with the Anthropic Claude Message API.

        Args:
            available_tools: The tools for mapping.

        Returns:
            A list of tools mapped to a compatible format for the Anthropic Claude Message API.
        """

        serialized_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": getattr(
                        tool,
                        "inputSchema",
                        {"type": "object", "properties": {}}
                    )
            }
            for tool in available_tools
        ]

        return serialized_tools