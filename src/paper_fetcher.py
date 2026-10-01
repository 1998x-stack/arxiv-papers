# src/paper_fetcher.py
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import feedparser
import logging
from typing import List, Dict, Any

class PaperFetcher:
     """Fetches the latest papers from arXiv."""

     BASE_URL = 'http://export.arxiv.org/api/query?'

     def __init__(self):
         """Initialize the PaperFetcher instance."""
         self.query = 'cat:cs.LG+OR+cat:cs.AI+OR+cat:cs.NE+OR+cat:cs.CV'
         self.max_results = 50  # Fetch 50 papers at a time
         logging.debug("PaperFetcher instance created.")

     def fetch_latest_papers(self) -> List[Dict[str, Any]]:
         """Fetch the latest papers based on the query."""
         query = f'search_query={self.query}&sortBy=lastUpdatedDate&max_results={self.max_results}'
         url = self.BASE_URL + query
         logging.info(f"Fetching papers from URL: {url}")
         
         try:
             feed = feedparser.parse(url)
             
             # Check if the feed was parsed successfully
             if not hasattr(feed, 'entries') or not feed.entries:
                 logging.warning(f"No entries found in feed from {url}")
                 return []
             
             papers = []
             for entry in feed.entries:
                 # Validate required fields exist
                 if not hasattr(entry, 'title') or not hasattr(entry, 'summary'):
                     logging.warning(f"Skipping entry with missing title or summary: {getattr(entry, 'id', 'Unknown ID')}")
                     continue
                     
                 paper = {
                     'id': getattr(entry, 'id', ''),
                     'title': getattr(entry, 'title', ''),
                     'summary': getattr(entry, 'summary', ''),
                     'authors': [author.name for author in getattr(entry, 'authors', [])],
                     'published': getattr(entry, 'published', ''),
                     'link': getattr(entry, 'link', '')
                 }
                 papers.append(paper)
             logging.info(f"Fetched {len(papers)} papers successfully.")
             return papers
         except Exception as e:
             logging.error(f"Error fetching papers from {url}: {e}")
             return []