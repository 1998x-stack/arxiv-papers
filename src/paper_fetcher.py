# src/paper_fetcher.py
import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import feedparser
import logging

class PaperFetcher:
    """Fetches the latest papers from arXiv."""

    BASE_URL = 'http://export.arxiv.org/api/query?'

    def __init__(self):
        """Initialize the PaperFetcher instance."""
        self.query = 'cat:cs.LG+OR+cat:cs.AI+OR+cat:cs.NE+OR+cat:cs.CV'
        self.max_results = 50  # Fetch 50 papers at a time
        logging.debug("PaperFetcher instance created.")

    def fetch_latest_papers(self):
        """Fetch the latest papers based on the query."""
        query = f'search_query={self.query}&sortBy=lastUpdatedDate&max_results={self.max_results}'
        url = self.BASE_URL + query
        logging.info(f"Fetching papers from URL: {url}")
        feed = feedparser.parse(url)
        papers = []
        for entry in feed.entries:
            paper = {
                'id': entry.id,
                'title': entry.title,
                'summary': entry.summary,
                'authors': [author.name for author in entry.authors],
                'published': entry.published,
                'link': entry.link
            }
            papers.append(paper)
        logging.info(f"Fetched {len(papers)} papers.")
        return papers