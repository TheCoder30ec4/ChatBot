from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from app.api import register_routers

app = FastAPI(title="Tool Server")

register_routers(app)

mcp = FastApiMCP(app, name="Tool server MCP", description="MCP tools for the ChatBot")
mcp.mount()
