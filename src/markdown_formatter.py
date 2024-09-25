# src/markdown_formatter.py
import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import markdown

class MarkdownFormatter:
    """Formats paper data into HTML for emails."""

    @staticmethod
    def format_papers(papers):
        markdown_content = ''
        for paper in papers:
            markdown_content += f"### [{paper['title']}]({paper['link']})\n"
            markdown_content += f"*Authors*: {', '.join(paper['authors'])}\n\n"
            markdown_content += f"{paper['summary']}\n\n"
        # Convert Markdown to HTML
        html_content = markdown.markdown(markdown_content)
        return html_content