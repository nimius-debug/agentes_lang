# tools.py

import requests
from langchain_core.tools import tool

# Placeholder for Tabily's search function
def tabily_search(query: str) -> str:
    """Search the web using Tabily."""
    # Replace the following code with Tabily's actual API call
    # For now, we'll just return a placeholder string
    return f"Results for '{query}' from Tabily."

# Define the tool using LangChain's @tool decorator
@tool
def web_search(query: str) -> str:
    """Use Tabily to search the web."""
    return tabily_search(query)
