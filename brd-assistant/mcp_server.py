# BRD Assistant - MCP Server
# Exposes our 4 BRD tools so ANY MCP app (e.g. Claude Desktop) can use them.

from mcp.server import MCPServer

import tools as brd   # our 4 functions from tools.py

mcp = MCPServer("BRD Assistant")


@mcp.tool()
def search_brd(question: str) -> str:
    """Answer a question about the ShopEasy BRD: business rules, limits, timeouts,
    payment, refund, cart or login requirements. Returns the answer with requirement IDs."""
    return brd.search_brd(question)


@mcp.tool()
def generate_stories(module: str) -> str:
    """Generate user stories with Given-When-Then acceptance criteria for ONE BRD module.
    module must be one of: Login, Cart, Payment, Refund. Returns the stories as JSON."""
    return brd.generate_stories(module)


@mcp.tool()
def save_stories(module: str) -> str:
    """Save the user stories that were just generated for a module. Call AFTER generate_stories."""
    # Guard: generate first if nothing was generated yet (same fix as in agent.py)
    if module.lower() not in brd._last_generated:
        brd.generate_stories(module)
    return brd.save_stories(module)


@mcp.tool()
def list_stories(module: str = "") -> str:
    """List saved user stories. Give a module name (Login, Cart, Payment, Refund) or leave empty for all."""
    return brd.list_stories(module)


if __name__ == "__main__":
    mcp.run()   # start the server and wait for an MCP app to connect