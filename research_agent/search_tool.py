from tavily import TavilyClient
from typing import List, Dict, Any
from loguru import logger
from .config import config

class SearchTool:
    def __init__(self, api_key: str = None):
        self.client = TavilyClient(api_key=api_key or config.tavily_api_key)
    
    async def search(self, query: str, max_results: int = None) -> List[Dict[str, Any]]:
        max_results = max_results or config.max_search_results_per_query
        try:
            response = self.client.search(query=query, max_results=max_results)
            results = []
            for res in response.get("results", []):
                results.append({
                    "title": res.get("title"),
                    "url": res.get("url"),
                    "content": res.get("content"),
                    "raw_content": res.get("raw_content")
                })
            logger.info(f"Search '{query}' → {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Search failed for '{query}': {e}")
            return []
