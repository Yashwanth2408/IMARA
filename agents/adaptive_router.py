"""
Adaptive routing with confidence scoring - NOVEL FEATURE
Routes queries to specialized agent paths based on complexity analysis
"""

from langchain_ollama import OllamaLLM
from typing import Dict, Literal

class AdaptiveRouter:
    """Routes queries intelligently based on complexity and domain analysis"""
    
    def __init__(self, llm: OllamaLLM):
        self.llm = llm
    
    def analyze_query(self, query: str) -> Dict:
        """Analyze query complexity, domain, and required expertise"""
        
        prompt = f"""Analyze this research query and provide scores (0-10):

Query: "{query}"

Provide scores for:
1. Technical Complexity (how specialized is the topic?)
2. Code Requirement (does it need code generation?)
3. Literature Depth (how much research needed?)
4. Novelty (how cutting-edge is this topic?)

Format: complexity:X, code:X, literature:X, novelty:X

Analysis:"""
        
        response = self.llm.invoke(prompt)
        
        # Parse scores
        scores = self._parse_scores(response)
        
        # Determine optimal path
        path = self._determine_path(scores)
        
        return {
            'scores': scores,
            'path': path,
            'confidence': self._calculate_confidence(scores)
        }
    
    def _parse_scores(self, response: str) -> Dict[str, int]:
        """Extract numerical scores from LLM response"""
        scores = {
            'complexity': 5,
            'code': 5,
            'literature': 5,
            'novelty': 5
        }
        
        try:
            # Simple parsing
            for key in scores.keys():
                if key in response.lower():
                    # Extract number after key
                    parts = response.lower().split(key)
                    if len(parts) > 1:
                        nums = [int(s) for s in parts[1].split() if s.isdigit()]
                        if nums:
                            scores[key] = min(nums[0], 10)
        except:
            pass
        
        return scores
    
    def _determine_path(self, scores: Dict[str, int]) -> str:
        """Determine optimal agent path based on scores"""
        
        if scores['complexity'] > 7 and scores['literature'] > 7:
            return "deep_research"  # Extra research agent pass
        elif scores['code'] > 7:
            return "code_focused"  # More emphasis on coding
        elif scores['novelty'] > 8:
            return "exploratory"  # Creative exploration
        else:
            return "standard"  # Normal workflow
    
    def _calculate_confidence(self, scores: Dict[str, int]) -> float:
        """Calculate confidence score for the routing decision"""
        avg_score = sum(scores.values()) / len(scores)
        # Higher average = higher confidence in understanding
        return round(avg_score / 10, 2)
