import asyncio

from app.api.manager import MCPManager
from app.workflow.input_books_workflow import InputBooksWorkflow
from app.llm.openai_service import OpenAIService

async def main():

    llm = OpenAIService()

    async with MCPManager() as mcp:
        workflow = InputBooksWorkflow(
            model = llm,
            mcp = mcp
        )
        
        try:
            await workflow.run()
        except Exception as e:
            print(e)

if __name__ == "__main__":
    asyncio.run(main())