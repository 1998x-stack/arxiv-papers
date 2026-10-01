"""Unit tests for the process_arxiv_metadata module."""

import unittest
from unittest.mock import patch, Mock, mock_open
from ai_paper.paper_fetch.process_arxiv_metadata import process_arxiv_metadata


class TestProcessArxivMetadata(unittest.TestCase):
    """Test suite for process_arxiv_metadata module."""

    @patch('ai_paper.paper_fetch.process_arxiv_metadata.os.path.exists')
    @patch('ai_paper.paper_fetch.process_arxiv_metadata.open')
    @patch('ai_paper.paper_fetch.process_arxiv_metadata.ThreadPoolExecutor')
    @patch('ai_paper.paper_fetch.process_arxiv_metadata.process_paper')
    @patch('ai_paper.paper_fetch.process_arxiv_metadata.tqdm')
    @patch('ai_paper.paper_fetch.process_arxiv_metadata.logger')
    def test_process_arxiv_metadata_success(self, mock_logger, mock_tqdm, mock_process_paper, 
                                           mock_executor_class, mock_open_func, mock_exists):
        """Test successful processing of arXiv metadata."""
        # Mock that file exists
        mock_exists.return_value = True
        
        # Mock file content (2 records)
        mock_file_content = ['{"id": "1", "title": "Paper 1"}\n', '{"id": "2", "title": "Paper 2"}\n']
        mock_file_handle = Mock()
        mock_file_handle.__iter__.return_value = iter(mock_file_content)
        mock_open_func.return_value.__enter__.return_value = mock_file_handle
        
        # Mock ThreadPoolExecutor
        mock_executor = Mock()
        mock_future1 = Mock()
        mock_future1.result.return_value = True  # Success
        mock_future2 = Mock()
        mock_future2.result.return_value = False  # Failure
        mock_executor.__enter__.return_value.submit.side_effect = [mock_future1, mock_future2]
        
        mock_executor_context = Mock()
        mock_executor_context.__enter__ = Mock(return_value=mock_executor)
        mock_executor_context.__exit__ = Mock(return_value=None)
        mock_executor_class.return_value = mock_executor_context
        
        # Mock tqdm
        mock_tqdm_instance = Mock()
        mock_tqdm_instance.__enter__.return_value = mock_tqdm_instance
        mock_tqdm.return_value = mock_tqdm_instance
        
        # Mock process_paper to return appropriate values
        mock_process_paper.side_effect = [True, False]
        
        # Call the function
        process_arxiv_metadata()
        
        # Verify the function was called properly
        mock_exists.assert_called_once()
        mock_open_func.assert_called_once()
        self.assertEqual(mock_executor.submit.call_count, 2)  # Called for each record
        mock_tqdm.assert_called_once_with(total=2, desc="处理论文")

    @patch('ai_paper.paper_fetch.process_arxiv_metadata.os.path.exists')
    @patch('ai_paper.paper_fetch.process_arxiv_metadata.logger')
    def test_process_arxiv_metadata_file_not_found(self, mock_logger, mock_exists):
        """Test handling when metadata file doesn't exist."""
        # Mock that file doesn't exist
        mock_exists.return_value = False
        
        # Call the function
        process_arxiv_metadata()
        
        # Verify error was logged
        mock_logger.error.assert_called_once()

    @patch('ai_paper.paper_fetch.process_arxiv_metadata.os.path.exists')
    @patch('ai_paper.paper_fetch.process_arxiv_metadata.open')
    @patch('ai_paper.paper_fetch.process_arxiv_metadata.logger')
    def test_process_arxiv_metadata_file_read_error(self, mock_logger, mock_open_func, mock_exists):
        """Test handling when metadata file can't be read."""
        # Mock that file exists
        mock_exists.return_value = True
        
        # Mock file opening to raise an exception
        mock_open_func.side_effect = IOError("Cannot read file")
        
        # Call the function
        process_arxiv_metadata()
        
        # Verify error was logged
        mock_logger.error.assert_called_once()


if __name__ == '__main__':
    unittest.main()