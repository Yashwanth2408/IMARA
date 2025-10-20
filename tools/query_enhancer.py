"""
Query enhancement for better ArXiv results
"""

class QueryEnhancer:
    """Enhance user queries for better search results"""
    
    def __init__(self):
        self.year_keywords = ["2024", "2025", "recent", "latest"]
    
    def enhance_query(self, query: str) -> str:
        """Add enhancement keywords to improve search quality"""
        
        # Add year constraint for recency
        if not any(year in query.lower() for year in self.year_keywords):
            query = f"{query} 2024 2025"
        
        # Add quality indicators
        query = f"{query} AND (abs:state-of-the-art OR abs:novel OR abs:recent)"
        
        return query
