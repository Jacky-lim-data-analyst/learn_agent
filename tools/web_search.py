from tavily import TavilyClient
from dotenv import load_dotenv
import os

def search(query: str) -> str:
    """Practical web search based on Tavily"""
    print(f"🔍 Executing [Tavily] web search: {query}")
    load_dotenv()
    try:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return "Error: Tavily api key not found"
        
        client = TavilyClient(api_key=api_key)
        results = client.search(query=query)

        results_list = results['results']
        if not results_list:
            return f"No web search results found for query: {query}" 

        result_text = []
        for content in results_list:
            text = content.get('title') + "\n" + content.get('content')
            result_text.append(text)
        return "\n\n".join(result_text)

    except Exception as exc:
        return f"Error during web search: {exc}"
        
if __name__ == "__main__":
    print(search("space race between US and China"))
    