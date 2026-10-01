"""Unit tests for the paper_processor module."""

import unittest
import json
from unittest.mock import patch, Mock, mock_open
from ai_paper.paper_fetch.paper_processor import process_paper


class TestPaperProcessor(unittest.TestCase):
    """Test suite for paper_processor module."""

    def test_process_paper_success(self):
        """Test successful processing of a paper."""
        paper_data = {
            'id': '1234.5678',
            'title': 'Test Paper',
            'summary': 'Test Summary',
            'categories': 'cs.LG cs.AI',
            'doi': '10.1234/example.doi'
        }
        
        line = json.dumps(paper_data)
        
        # Mock the parse_html function
        with patch('ai_paper.paper_fetch.paper_processor.parse_html', return_value={'parsed': 'data'}):
            # Mock the counts.citation_count function
            with patch('ai_paper.paper_fetch.paper_processor.counts') as mock_counts:
                mock_counts.citation_count.return_value = 42
                
                # Mock os.makedirs and file writing
                with patch('ai_paper.paper_fetch.paper_processor.os.makedirs'):
                    with patch('builtins.open', mock_open()):
                        result = process_paper(line)
        
        # Verify successful processing
        self.assertTrue(result)

    def test_process_paper_missing_id(self):
        """Test processing a paper with missing ID."""
        paper_data = {
            'title': 'Test Paper',  # Missing 'id'
            'summary': 'Test Summary'
        }
        
        line = json.dumps(paper_data)
        
        result = process_paper(line)
        
        # Should return False when ID is missing
        self.assertFalse(result)

    def test_process_paper_no_doi(self):
        """Test processing a paper without DOI."""
        paper_data = {
            'id': '1234.5678',
            'title': 'Test Paper',
            'summary': 'Test Summary',
            'categories': 'cs.LG',
            'doi': None  # No DOI
        }
        
        line = json.dumps(paper_data)
        
        # Mock the parse_html function
        with patch('ai_paper.paper_fetch.paper_processor.parse_html', return_value={'parsed': 'data'}):
            # Mock os.makedirs and file writing
            with patch('ai_paper.paper_fetch.paper_processor.os.makedirs'):
                with patch('builtins.open', mock_open()):
                    result = process_paper(line)
        
        # Should still process successfully even without DOI
        self.assertTrue(result)

    def test_process_paper_citation_error(self):
        """Test processing when citation count fails."""
        paper_data = {
            'id': '1234.5678',
            'title': 'Test Paper',
            'summary': 'Test Summary',
            'categories': 'cs.LG',
            'doi': '10.1234/example.doi'
        }
        
        line = json.dumps(paper_data)
        
        # Mock the parse_html function
        with patch('ai_paper.paper_fetch.paper_processor.parse_html', return_value={'parsed': 'data'}):
            # Mock counts.citation_count to raise an exception
            with patch('ai_paper.paper_fetch.paper_processor.counts') as mock_counts:
                mock_counts.citation_count.side_effect = Exception("Citation service error")
                
                # Mock os.makedirs and file writing
                with patch('ai_paper.paper_fetch.paper_processor.os.makedirs'):
                    with patch('builtins.open', mock_open()):
                        result = process_paper(line)
        
        # Should still process successfully despite citation error
        self.assertTrue(result)

    def test_process_paper_json_error(self):
        """Test processing with invalid JSON."""
        invalid_line = '{"id": "1234.5678", "title": "Unclosed quote}'  # Invalid JSON
        
        result = process_paper(invalid_line)
        
        # Should return False on JSON decode error
        self.assertFalse(result)

    def test_process_paper_general_error(self):
        """Test processing with a general error."""
        paper_data = {
            'id': '1234.5678',
            'title': 'Test Paper',
            'summary': 'Test Summary'
        }
        
        line = json.dumps(paper_data)
        
        # Mock to raise an exception during processing
        with patch('ai_paper.paper_fetch.paper_processor.parse_html', side_effect=Exception("Processing error")):
            result = process_paper(line)
        
        # Should return False on general error
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()