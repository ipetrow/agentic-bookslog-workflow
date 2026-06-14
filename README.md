# Project Overview
This project presents a multi-step agentic AI workflow built around MCP, OpenAI Responses API, SQLite and Python. It demonstrates the utilization of an LLM, provided with external capabilities (e.g., tools and resources), for automating document data retrieval and the further application of the extracted data. Furthermore, it explored the topic of evaluation testing for ensuring the accuracy and reliability of the workflow.

# Use Case
The workflow aims to ease the update of a user's digital record/log of owned books. The books' information is automatically extracted from a receipt pdf document and, in a subsequent step, inserted into a dedicated database, functioning as a personal library.

# Implementation Scope
The goals of the implementation was to explore the following topics:
- Managing more than one MCP Server sessions.
- Utilising different MCP server primitive types.
- Coordinating multiple workflow steps.
- Keeping the LLM and API layers loosely coupled.

One of the main implementation objectives was the separation of concerns for all the layers. This allows flexibility in migrating to another LLM solution or, when useful, using different models for each of the workflow steps.

## Out of Scope
- A user interaction interface: The prompts are pre-defined and, where necessary, built at runtime according to the retrieved information from previous steps. 
- Extracting data from multiple files: The workflow handles a single pdf document. 

# Project Structure
The project consists of the following directories:
- `app`: The main directory containing all the project files. It is a Python module providing the entry point for the application `__main__.py`.
- `workflow`: Contains the workflow steps and their logical execution sequence. 
- `api`: Contains the MCP Client-Server logic - client-server session creation and management, handling server primitives access.
- `llm`: Contains the logic related with the model - api calls, formatting the data passed to the model. 
- `tests`: Constains the evalution tests ensuring the accurancy and reliability of the workflow and its two main steps. 

# Prerequisites
- Installed Python `uv` package and project management tool. A basic understanding of how the tool works would be helpful for a better insight of how the project is set up and executed.
- Installed Python version 3.14.2 or higher.
- An OpenAI API key included in the environment variables.

# Implementation Details

## Workflow
The workflow consists of 2 main steps:
1. Step 1, Data  Extraction: Extract the information about all the purchased books listed in a receipt PDF file.
2. Step 2, Data Insertion: Inserts the extracted information in Step 1 into a dedicated database storing books' data.

Each step is decoupled from the rest and separated in its own file. This promotes code testability.

## API
For the API layer, a MCP Client-Server standard is being used. The MCP Servers are created using `FastMCP` with `stdio` as transport layer. 

### Servers
There are two MCP Servers, each one with its own responsibility:
1. Database server: A MCP Server exposing tools for interacting with the `bookslog` database. 
- Server file path `app/api/servers/database/database_server.py`.
- Server resource: A `bookslog.db` database (pre-filled with 3 entries) situated in the same folder.
- Server primitives: a couple of tools `get_books() -> str` and `insert_books(book: list[Book]) -> None`.
2. Files server: A MCP Server exposing a file as a resource. It is situated in `app/api/servers/files/database_server.py`.
- Server file path `app/api/servers/files/database_server.py`.
- Server resource: A PDF file representing a receipt for 3 situated in the same folder.
- Server primitives: A single resource `file://receipts/receipt-001.pdf`.

The information for connecting to the servers is extracted and read from the `server_config.json` file.

## LLM
The OpenAI `gpt-5-mini` model is used from Azure - The GPT model was deployed in Azure and the Azure OpenAI API key used for the connection with the LLM. This integration allows the User to interact on an abstract level with the tools exposed from the MCP Server.

This layer further uses the
- OpenAI Python API: The library provides access to the OpenAI REST API.
- OpenAI Responses API: An interface for interacting with the LLM.

One of the main objectives for the project was to decouple the `llm` layer from the `api` and `workflow` layers. This is achieved with the help of a mapping class `OpenAIContextMapper`. This approach allows an easy migration to another LLM API (e.g., Anthropic Claude API).

## Database
It is a simplistic sqlite database named ***bookslog***, consisting of only one table - ***books***. The main idea is to store books information - ***isbn***, ***title***, ***author*** and ***number of pages***. For convenience and simplicity of the demo, a book can have only one author stored as a string.

The database path for the production application is set in the `.env` file and loaded right at the beginning of the application start.

# Running the Project
## Setup
1. Clone the repository: `git@github.com:ipetrow/agentic_bookslog.git`.
2. Sync the project in order to download and install all the required project dependencies and they are up to date: `uv sync`. This will create the project virtual environment (`.venv`) as well.
3. Update the model name in `app/llm/openai_service.py` by providing a value for the `MODEL` constant.
4. Update the Azure endpoint in `app/llm/openai_service.py` by providing a value for the `ENDPOINT` constant.
5. Double check the OpenAI API key is added in the environment variables. The name of the variable is `OPENAI_API_KEY` and retrieved in `app/llm/openai_service.py`.

## Execution
Start the MCP Client and connect to the MCP Server by: `uv run python -m app`.

# Evaluation Tests
There are 3 evaluation tests implemented
1. `test_input_books_workflow.py`: evaluates the output of the whole workflow.
2. `test_extract_books_data_step.py`: evaluates in isolation the step extracting the book data from the file.
3. `test_insert_books_step.py`: evaluates in isolation the step inserting the book data to the database.

## Implementation Details
- The implementation utilizes the functionalities and capabilities provided by the Python `pytest` library.
- The tests are working with a dedicated test database `tests/evals/bookslog.db` separate from the production database.
- The database path is set in the `.env.test` file. The configuration is handled in the `tests/conftest.py`.

## Execution
- For executing one of the tests: `uv run python -m pytest tests/evals/test_extract_books_data_step.py`.
- For executing all tests: `uv run python -m pytest`.

# References
1. The project is an evolution of two earlier repositories where I explored the [MCP Database Manipulation](https://github.com/ipetrow/mcp-database-demo) and the [File Data Retrieval](https://github.com/ipetrow/mcp-files-demo) topics in isolation.
2. Python [pytest](https://docs.pytest.org) library official documentation.
