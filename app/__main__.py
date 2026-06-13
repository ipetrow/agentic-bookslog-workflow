import asyncio

from dotenv import load_dotenv

from app.api.manager import MCPManager
from app.workflow.input_books_workflow import InputBooksWorkflow
from app.llm.openai_service import OpenAIService

async def main():

    load_dotenv()

    llm = OpenAIService()

    async with MCPManager() as mcp:
        workflow = InputBooksWorkflow(
            model = llm,
            mcp = mcp
        )
        
        try:
            response = await workflow.run()

            print(f"Answer:\n\n{response}")

        except Exception as e:
            print(e)

if __name__ == "__main__":
    asyncio.run(main())