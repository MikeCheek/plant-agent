from smolagents.tools import Tool
import json
import os

class GardeningKnowledgeTool(Tool):
    """
    A tool that provides specific care instructions for plants based on a pre-loaded gardening manual.
    Args:
        query (`str`): The plant name to search for in the gardening manual.
    Examples:
        ```python
        >>> result = gardening_tool("Fiddle Leaf Fig")
        >>> print(result)
        ```
    """
    name = "gardening_manual"
    description = "Retrieves specific care instructions for plants. Handles ONLY plant names as input."
    inputs = {'query': {'type': 'string', 'description': 'The plant name to search for.'}}
    output_type = "string"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._retriever = None
        self._raw_data = []

    def _build_retriever(self):
        # Imports inside tool for smolagents compatibility
        from langchain_core.documents import Document
        from langchain_community.retrievers import BM25Retriever

        if not os.path.exists("data/plants_data.json"):
            return "Error: data/plants_data.json not found."

        with open("data/plants_data.json", "r") as f:
            self._raw_data = json.load(f)

        docs = []
        for p in self._raw_data:
            # Create a rich text block for the BM25 search engine to index
            rich_content = (
                f"Name: {p.get('name', 'Unknown')}. "
                f"Description: {p.get('description', '')}. "
                f"Details: {p.get('waterFrequency', '')}, {p.get('soilType', '')}, "
                f"{p.get('idealPeriod', '')}, {p.get('exposition', '')}. "
                f"Curiosity: {p.get('curiosity', '')}"
            )
            docs.append(
                Document(
                    page_content=rich_content,
                    metadata={"name": p.get("name", "").lower()}
                )
            )

        # k=1 because we want the most specific match for a plant query
        self._retriever = BM25Retriever.from_documents(docs, k=2)

    def forward(self, query: str) -> str:
        import difflib # For similarity matching
        
        if self._retriever is None:
            self._build_retriever()

        clean_query = query.lower().strip()
        
        # 1. Try a "Fuzzy Match" first for the exact plant name
        plant_names = [p['name'] for p in self._raw_data]
        matches = difflib.get_close_matches(clean_query, [n.lower() for n in plant_names], n=1, cutoff=0.6)
        
        # 2. If no direct fuzzy match, use the BM25 retriever
        if matches:
            # Find the full data for the fuzzy-matched name
            matched_name = matches[0]
            plant_info = next((p for p in self._raw_data if p['name'].lower() == matched_name), None)
            
            return self._format_plant_data(plant_info, source="Fuzzy Match")
        
        # 3. Fallback to BM25 if fuzzy match failed (helps with nicknames like "Rubber Plant")
        results = self._retriever.invoke(clean_query)
        if results:
            return f"Found via keyword search:\n{results[0].page_content}"

        return f"I couldn't find a manual entry for '{query}'. Try searching for the general plant family name."

    def _format_plant_data(self, p, source):
        return (
            f"--- MANUAL ENTRY FOUND ({source}) ---\n"
            f"🌿 NAME: {p.get('name')}\n"
            f"📝 DESCRIPTION: {p.get('description')}\n"
            f"💧 WATER: {p.get('waterFrequency')}\n"
            f"🌱 SOIL: {p.get('soilType')}\n"
            f"📅 BEST PERIOD: {p.get('idealPeriod')}\n"
            f"☀️ EXPOSITION: {p.get('exposition')}\n"
            f"🤔 CURIOSITY: {p.get('curiosity')}\n"
        )