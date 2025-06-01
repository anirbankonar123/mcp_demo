Cmd to run the chatbot with MCP Client: <br>
add the dependencies to uv using uv add , ex: uv add tavily-python, uv add langchain langchain-core langchain-community langchain-google-genai <br>
Add your GOOGLE_API_KEY and Tavily key respectively in image_extractor.py and web_extractor.py <br>
Add your ANTHROPIC KEY using export api_key= <br>
Use the pdfToImages.pf to extract images from your local PDF documents <br>
run the server first :uv run spaceScience_server.py <br>
run the MCP Client chatbot : uv run mcp_space_sse_chatbot.py <br>
To run the github pre-built MCP Server : uv run mcp_chatbot_multi_server.py <br>
