import arxiv
import requests
from pathlib import Path
import PyPDF2
from io import BytesIO
from datetime import datetime

try:
    from scholarly import scholarly
    SCHOLARLY_AVAILABLE = True
except ImportError:
    SCHOLARLY_AVAILABLE = False
    print("Warning: scholarly not installed. Google Scholar search disabled.")


class PaperSearchTool:
    """Search and download academic papers from multiple sources"""
    
    def __init__(self, max_results=7):
        self.max_results = max_results
        self.max_arxiv = 5
        self.max_scholar = 2  # Additional papers from Scholar
        self.download_dir = Path("data/papers")
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    def search_papers(self, query: str, recent_only: bool = False) -> list:
        """Search ArXiv and Google Scholar for papers"""
        papers = []
        
        # Search ArXiv (primary source)
        try:
            arxiv_papers = self._search_arxiv(query, self.max_arxiv)
            papers.extend(arxiv_papers)
        except Exception as e:
            print(f"ArXiv search error: {e}")
        
        # Search Google Scholar (supplementary) - Only if installed
        if SCHOLARLY_AVAILABLE:
            try:
                scholar_papers = self._search_google_scholar(query, self.max_scholar)
                papers.extend(scholar_papers)
            except Exception as e:
                print(f"Scholar search error: {e}")
        
        # Filter recent papers if requested
        if recent_only and papers:
            current_year = datetime.now().year
            papers = [p for p in papers if int(p['published'][:4]) >= current_year - 3]
        
        return papers[:self.max_results]
    
    def _search_arxiv(self, query: str, max_results: int) -> list:
        """Search ArXiv specifically"""
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        papers = []
        for result in search.results():
            papers.append({
                'title': result.title,
                'authors': [author.name for author in result.authors],
                'summary': result.summary[:500],
                'pdf_url': result.pdf_url,
                'published': result.published.strftime('%Y-%m-%d'),
                'source': 'arxiv'
            })
        
        return papers
    
    def _search_google_scholar(self, query: str, max_results: int) -> list:
        """Search Google Scholar for additional papers"""
        papers = []
        
        try:
            search_query = scholarly.search_pubs(query)
            
            for i, result in enumerate(search_query):
                if i >= max_results:
                    break
                
                bib = result.get('bib', {})
                
                # Handle authors properly
                authors = bib.get('author', [])
                if isinstance(authors, str):
                    authors = [authors]
                elif not isinstance(authors, list):
                    authors = ['Unknown']
                
                # Handle year
                year = bib.get('pub_year', '2024')
                if isinstance(year, int):
                    year = str(year)
                
                papers.append({
                    'title': bib.get('title', 'Unknown'),
                    'authors': authors,
                    'summary': bib.get('abstract', 'No abstract available')[:500],
                    'pdf_url': result.get('pub_url', ''),
                    'published': f"{year}-01-01",
                    'source': 'scholar'
                })
        except Exception as e:
            print(f"Scholar detailed error: {e}")
        
        return papers
    
    def download_and_extract(self, pdf_url: str, filename: str) -> str:
        """Download PDF and extract text"""
        try:
            response = requests.get(pdf_url, timeout=30)
            pdf_file = BytesIO(response.content)
            
            # Save PDF
            save_path = self.download_dir / filename
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            # Extract text
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages[:5]:  # First 5 pages
                text += page.extract_text()
            
            return text[:3000]  # Return first 3000 chars
        except Exception as e:
            return f"Error extracting PDF: {str(e)}"
    
    def format_paper_summary(self, papers: list) -> str:
        """Format papers into readable summary"""
        if not papers or (len(papers) > 0 and 'error' in papers[0]):
            return "No papers found or error occurred."
        
        summary = "## Found Research Papers:\n\n"
        for i, paper in enumerate(papers, 1):
            source_badge = "📄 ArXiv" if paper.get('source') == 'arxiv' else "🎓 Scholar"
            summary += f"**{i}. {paper['title']}** {source_badge}\n"
            
            # Handle authors properly
            authors = paper.get('authors', ['Unknown'])
            if isinstance(authors, list):
                author_str = ', '.join(authors[:3])
            else:
                author_str = str(authors)
            
            summary += f"   - Authors: {author_str}\n"
            summary += f"   - Published: {paper['published']}\n"
            summary += f"   - Summary: {paper['summary'][:200]}...\n\n"
        
        return summary
