# src/markdown_formatter.py
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import markdown
import logging
from typing import List, Dict, Any

class MarkdownFormatter:
     """Formats paper data into HTML for emails."""

     @staticmethod
     def format_papers(papers: List[Dict[str, Any]]) -> str:
         markdown_content = ''
         for paper in papers:
             # Sanitize title to prevent markdown injection
             title = paper['title'].replace('[', '\\[').replace(']', '\\]').replace('(', '\\(').replace(')', '\\)')
             # Remove or escape other problematic characters
             title = title.replace('<', '&lt;').replace('>', '&gt;')
             markdown_content += f"### [{title}]({paper['link']})\n"
             # Sanitize authors list
             authors = [author.replace('<', '&lt;').replace('>', '&gt;') for author in paper['authors']]
             markdown_content += f"*Authors*: {', '.join(authors)}\n\n"
             # Sanitize summary
             summary = paper['summary'].replace('<', '&lt;').replace('>', '&gt;')
             markdown_content += f"{summary}\n\n"
         # Convert Markdown to HTML
         html_content = markdown.markdown(markdown_content)
         return html_content