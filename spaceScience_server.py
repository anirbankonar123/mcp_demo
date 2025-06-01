import arxiv
import json
import os
from typing import List
from mcp.server.fastmcp import FastMCP

from image_extractor import ImageExtractor
from web_extractor import WebExtractor


webExt = WebExtractor()
imageExt = ImageExtractor()


IMAGES_DIR = "images/An_Introduction_to_Space_Exploration_TPDas"
IMAGES_DIR1 = "images/Solar_System_Exploration_and_India_contributions"
IMAGES_DIR2 = "images/The_Lunar_Saga_edition2"

# Initialize FastMCP server
mcp = FastMCP("space_research", port=8001)

@mcp.tool()
def search_images(query: str) -> List[str]:
    """
    Search the images from a pdf for the topic and return the result

    Args:
        query: The query to search for

    Returns:
        result of the query found in the search
    """

    response = imageExt.get_response(query, IMAGES_DIR)
    response1 = imageExt.get_response(query, IMAGES_DIR1)
    response2 = imageExt.get_response(query, IMAGES_DIR2)

    return response+" "+response1+" "+response2


@mcp.tool()
def search_web(query: str) -> str:
    """
    Search for information about a space science query using tavily web search.

    Args:
        query: The space science query

    Returns:
        answer to the query
    """

    response = webExt.get_response(query)

    return response


@mcp.resource("images://folders")
def get_available_folders() -> str:
    """
    List all available images folders in the images directory.

    This resource provides a simple list of all available images folders.
    """
    folders = []

    # Get all topic directories
    if os.path.exists("images"):
        for topic_dir in os.listdir("images"):
            folders.append(topic_dir)


    # Create a simple markdown list
    content = "# Available Documents\n\n"
    for folder in folders:
        content+=folder+"\n"

    return content

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='sse')
