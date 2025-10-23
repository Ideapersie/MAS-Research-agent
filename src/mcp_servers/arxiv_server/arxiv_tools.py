"""
ArXiv API Tools for searching and fetching research papers.
"""
import requests
import feedparser
from typing import List, Dict, Optional
from datetime import datetime


class ArxivSearchTool:
    """Tool for searching ArXiv papers."""

    def __init__(self, api_base: str = "http://export.arxiv.org/api/query", max_results: int = 20):
        self.api_base = api_base
        self.max_results = max_results

    def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        sort_by: str = "relevance",
        sort_order: str = "descending"
    ) -> List[Dict]:
        """
        Search ArXiv for papers matching the query.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            sort_by: Sort criterion (relevance, lastUpdatedDate, submittedDate)
            sort_order: Sort order (ascending, descending)

        Returns:
            List of paper dictionaries with metadata
        """
        max_results = max_results or self.max_results

        # Build query parameters
        params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': max_results,
            'sortBy': sort_by,
            'sortOrder': sort_order
        }

        try:
            response = requests.get(self.api_base, params=params, timeout=30)
            response.raise_for_status()

            # Parse the XML response using feedparser
            feed = feedparser.parse(response.content)

            papers = []
            for entry in feed.entries:
                paper = {
                    'title': entry.title,
                    'arxiv_id': entry.id.split('/abs/')[-1],
                    'summary': entry.summary,
                    'authors': [author.name for author in entry.authors],
                    'published': entry.published,
                    'updated': entry.updated,
                    'pdf_url': entry.id.replace('/abs/', '/pdf/') + '.pdf',
                    'abs_url': entry.id,
                    'categories': [tag.term for tag in entry.tags] if hasattr(entry, 'tags') else [],
                    'primary_category': entry.arxiv_primary_category.term if hasattr(entry, 'arxiv_primary_category') else None
                }
                papers.append(paper)

            return papers

        except requests.RequestException as e:
            raise Exception(f"ArXiv API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to parse ArXiv response: {str(e)}")

    def search_by_author(self, author_name: str, max_results: Optional[int] = None) -> List[Dict]:
        """Search ArXiv papers by author name."""
        max_results = max_results or self.max_results

        params = {
            'search_query': f'au:{author_name}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }

        try:
            response = requests.get(self.api_base, params=params, timeout=30)
            response.raise_for_status()
            feed = feedparser.parse(response.content)

            papers = []
            for entry in feed.entries:
                paper = {
                    'title': entry.title,
                    'arxiv_id': entry.id.split('/abs/')[-1],
                    'summary': entry.summary,
                    'authors': [author.name for author in entry.authors],
                    'published': entry.published,
                    'pdf_url': entry.id.replace('/abs/', '/pdf/') + '.pdf',
                    'abs_url': entry.id
                }
                papers.append(paper)

            return papers

        except Exception as e:
            raise Exception(f"Author search failed: {str(e)}")

    def get_paper_details(self, arxiv_id: str) -> Dict:
        """
        Get detailed information about a specific paper by ArXiv ID.

        Args:
            arxiv_id: ArXiv paper ID (e.g., "2301.12345")

        Returns:
            Dictionary with paper details
        """
        params = {
            'id_list': arxiv_id,
            'max_results': 1
        }

        try:
            response = requests.get(self.api_base, params=params, timeout=30)
            response.raise_for_status()
            feed = feedparser.parse(response.content)

            if not feed.entries:
                raise Exception(f"Paper with ID {arxiv_id} not found")

            entry = feed.entries[0]
            paper = {
                'title': entry.title,
                'arxiv_id': entry.id.split('/abs/')[-1],
                'summary': entry.summary,
                'authors': [author.name for author in entry.authors],
                'published': entry.published,
                'updated': entry.updated,
                'pdf_url': entry.id.replace('/abs/', '/pdf/') + '.pdf',
                'abs_url': entry.id,
                'categories': [tag.term for tag in entry.tags] if hasattr(entry, 'tags') else [],
                'primary_category': entry.arxiv_primary_category.term if hasattr(entry, 'arxiv_primary_category') else None,
                'comment': entry.arxiv_comment if hasattr(entry, 'arxiv_comment') else None,
                'journal_ref': entry.arxiv_journal_ref if hasattr(entry, 'arxiv_journal_ref') else None,
                'doi': entry.arxiv_doi if hasattr(entry, 'arxiv_doi') else None
            }

            return paper

        except Exception as e:
            raise Exception(f"Failed to get paper details: {str(e)}")


def format_papers_for_agent(papers: List[Dict]) -> str:
    """
    Format paper results into a readable string for LLM agents.

    Args:
        papers: List of paper dictionaries

    Returns:
        Formatted string with paper information
    """
    if not papers:
        return "No papers found."

    formatted = f"Found {len(papers)} paper(s):\n\n"

    for i, paper in enumerate(papers, 1):
        formatted += f"**Paper {i}:**\n"
        formatted += f"Title: {paper['title']}\n"
        formatted += f"ArXiv ID: {paper['arxiv_id']}\n"
        formatted += f"Authors: {', '.join(paper['authors'][:3])}"
        if len(paper['authors']) > 3:
            formatted += f" et al. ({len(paper['authors'])} authors total)"
        formatted += f"\n"
        formatted += f"Published: {paper['published']}\n"
        formatted += f"Categories: {', '.join(paper.get('categories', []))}\n"
        formatted += f"Abstract: {paper['summary'][:300]}...\n"
        formatted += f"URL: {paper['abs_url']}\n"
        formatted += f"PDF: {paper['pdf_url']}\n"
        formatted += "\n---\n\n"

    return formatted
