"""
Research Quality Metrics - NOVEL FEATURE
Tracks and scores research quality across multiple dimensions
"""

from datetime import datetime
from typing import Dict, List
import json
from pathlib import Path

class ResearchMetrics:
    """Track and analyze research quality metrics"""
    
    def __init__(self):
        self.metrics_file = Path("data/metrics.json")
        self.metrics_file.parent.mkdir(exist_ok=True)
    
    def calculate_paper_quality(self, papers: List[Dict]) -> Dict:
        """Calculate quality score for retrieved papers"""
        
        if not papers or 'error' in papers[0]:
            return {'score': 0, 'grade': 'F', 'issues': ['No papers found']}
        
        scores = {
            'recency': self._score_recency(papers),
            'relevance': self._score_relevance(papers),
            'citation_potential': self._score_authors(papers),
            'diversity': self._score_diversity(papers)
        }
        
        overall = sum(scores.values()) / len(scores)
        
        return {
            'overall_score': round(overall, 2),
            'grade': self._assign_grade(overall),
            'breakdown': scores,
            'paper_count': len(papers),
            'timestamp': datetime.now().isoformat()
        }
    
    def _score_recency(self, papers: List[Dict]) -> float:
        """Score based on publication dates (newer = better) with exponential weighting"""
        current_year = datetime.now().year
        years = []
    
        for paper in papers:
            try:
                year = int(paper.get('published', '2020')[:4])
                years.append(year)
            except:
                years.append(2020)
    
        # Exponential weighting: 2025 papers get 10/10, 2024 get 8/10, 2023 get 6/10, etc.
        scores = []
        for year in years:
            age = current_year - year
            if age == 0:  # Current year
                scores.append(10)
            elif age == 1:  # Last year
                scores.append(9)
            elif age == 2:
                scores.append(7)
            elif age == 3:
                scores.append(5)
            else:  # 4+ years old
                scores.append(max(1, 10 - age * 1.5))  # Degrade faster for older papers
    
        avg_score = sum(scores) / len(scores) if scores else 5.0
        return round(min(avg_score, 10), 1)
    
    def _score_relevance(self, papers: List[Dict]) -> float:
        """Score based on summary length and quality"""
        avg_summary_len = sum(len(p.get('summary', '')) for p in papers) / len(papers)
        # Longer summaries often indicate more relevant results
        relevance = min(avg_summary_len / 500, 1.0)
        return round(relevance * 10, 1)
    
    def _score_authors(self, papers: List[Dict]) -> float:
        """Score based on author count and paper structure"""
        if not papers:
            return 5.0
    
        scores = []
        for paper in papers:
            authors = paper.get('authors', [])
            author_count = len(authors)
        
            # Optimal range: 3-6 authors (collaborative but not too many)
            if 3 <= author_count <= 6:
                score = 10
            elif 2 <= author_count <= 8:
                score = 8
            elif author_count >= 9:
                score = 7  # Very large teams (might be less focused)
            else:  # 1 author
                score = 6  # Solo work (less peer validation)
        
            # Bonus: Check if authors include known patterns (affiliations)
            # This is a simplified heuristic
            scores.append(score)
    
        avg_score = sum(scores) / len(scores) if scores else 5.0
        return round(min(avg_score, 10), 1)

    
    def _score_diversity(self, papers: List[Dict]) -> float:
        """Score based on title diversity"""
        titles = [p.get('title', '') for p in papers]
        unique_words = set(' '.join(titles).lower().split())
        diversity = min(len(unique_words) / 50, 1.0)
        return round(diversity * 10, 1)
    
    def _assign_grade(self, score: float) -> str:
        """Assign letter grade"""
        if score >= 9: return 'A+'
        elif score >= 8: return 'A'
        elif score >= 7: return 'B+'
        elif score >= 6: return 'B'
        elif score >= 5: return 'C'
        else: return 'D'
    
    def save_metrics(self, metrics: Dict, query: str):
        """Save metrics to file"""
        data = {
            'query': query,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }
        
        # Append to metrics log
        existing = []
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                existing = json.load(f)
        
        existing.append(data)
        
        with open(self.metrics_file, 'w') as f:
            json.dump(existing, f, indent=2)
