"""Building a general tool executor
When an agent needs to use multiple tools, we need a unified 
manager to register and dispatch those tools"""

from typing import Any
from .web_search import search

class ToolExecutor:
    """
    A tool executor responsible for managing and executing tools.
    """
    def __init__(self) -> None:
        self.tools: dict[str, dict[str, Any]] = {}

    def register_tool(self, name: str, description: str, func: callable):
        """
        Register a new tool in the toolbox
        """
        if name in self.tools:
            print(f"Warning: Tool '{name}' already exists and will be overwritten")
        self.tools[name] = {'description': description, 'func': func}
        print(f"Tool '{name}' registered")

    def get_tool(self, name: str) -> callable:
        """
        Get a tool's execution function by name.
        """
        return self.tools.get(name, {}).get("func")
    
    def get_available_tools(self) -> str:
        """
        Get a formatted description string of all available tools.
        """
        return "\n".join([
            f"- {name}: {info["description"]}"
            for name, info in self.tools.items()
        ])
    
if __name__ == "__main__":
    # initialize a tool executor
    toolExecutor = ToolExecutor()

    # register our practical searc tool
    search_description = (
        "A web search engine. Use this tool when you need to answer questions about "
        "current events, facts, and information not found in your knowledge base."
    )
    toolExecutor.register_tool("Search", description=search_description, func=search)

    # print available tools
    print("\n--- Available Tools ---")
    print(toolExecutor.get_available_tools())

    # agent's action call 
    print("\n--- Execute Action: Search['What is NVIDIA's latest GPU model'] ---")
    tool_name = "Search"
    tool_input = "What is NVIDIA's latest GPU model"

    tool_function = toolExecutor.get_tool(tool_name)
    if tool_function:
        obs = tool_function(tool_input)
        print("--- Observation ---")
        print(obs)
    else:
        print(f"Error: Tool name '{tool_name}' not found")
