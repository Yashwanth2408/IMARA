from langchain_core.messages import AIMessage
from langchain_ollama import OllamaLLM
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from tools.paper_tools import PaperSearchTool
from tools.metrics import ResearchMetrics
from tools.query_enhancer import QueryEnhancer

class EnhancedResearcherAgent:
    """Researcher agent with ArXiv paper search"""
    
    def __init__(self, llm: OllamaLLM):
        self.llm = llm
        self.paper_tool = PaperSearchTool(max_results=7)
        self.query_enhancer = QueryEnhancer()
    
    def research(self, query: str) -> dict:
        """Perform comprehensive research with quality metrics"""

        # Enhance query for better results
        enhanced_query = self.query_enhancer.enhance_query(query) 

        # Search papers
        papers = self.paper_tool.search_papers(enhanced_query)
        paper_summary = self.paper_tool.format_paper_summary(papers)
    
        # Calculate quality metrics
        metrics_tracker = ResearchMetrics()
        quality_metrics = metrics_tracker.calculate_paper_quality(papers)
        metrics_tracker.save_metrics(quality_metrics, query)
    
        # Generate LLM summary
        prompt = f"""Based on these {len(papers)} academic papers (Quality Grade: {quality_metrics['grade']}), provide a comprehensive summary about "{query}":

    {paper_summary}

    Summary:"""
    
        llm_summary = self.llm.invoke(prompt)
    
        result = {
            'papers': papers,
            'paper_summary': paper_summary,
            'llm_summary': llm_summary,
            'quality_metrics': quality_metrics,
            'full_summary': f"**Research Quality: {quality_metrics['grade']} ({quality_metrics['overall_score']}/10)**\n\n{paper_summary}\n\n**Analysis:**\n{llm_summary}"
        }
    
        return result

