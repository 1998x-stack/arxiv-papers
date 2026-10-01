"""Unit tests for the ai_paper config module."""

import unittest
import os
from unittest.mock import patch
from ai_paper.paper_fetch.config import (
    PROJECT_ROOT, DATA_DIR, ARXIV_METADATA_PATH, 
    ARXIV_PROCESSED_DIR, LOG_DIR, ARXIV_PROCESSING_LOG,
    AR5IV_BASE_URL, AR5IV_IMAGE_BASE_URL, MAX_WORKER_THREADS,
    TASK_QUEUE_SIZE, HTML_FETCH_RETRIES, HTML_FETCH_TIMEOUT,
    DEFAULT_CATEGORY, DEFAULT_SUBCATEGORY, DEFAULT_YEAR, DEFAULT_MONTH
)


class TestConfig(unittest.TestCase):
    """Test suite for ai_paper config module."""

    def test_constants_defined(self):
        """Test that all required constants are defined."""
        self.assertIsInstance(PROJECT_ROOT, str)
        self.assertIsInstance(DATA_DIR, str)
        self.assertIsInstance(ARXIV_METADATA_PATH, str)
        self.assertIsInstance(ARXIV_PROCESSED_DIR, str)
        self.assertIsInstance(LOG_DIR, str)
        self.assertIsInstance(ARXIV_PROCESSING_LOG, str)
        self.assertIsInstance(AR5IV_BASE_URL, str)
        self.assertIsInstance(AR5IV_IMAGE_BASE_URL, str)
        self.assertIsInstance(MAX_WORKER_THREADS, int)
        self.assertIsInstance(TASK_QUEUE_SIZE, int)
        self.assertIsInstance(HTML_FETCH_RETRIES, int)
        self.assertIsInstance(HTML_FETCH_TIMEOUT, int)
        self.assertIsInstance(DEFAULT_CATEGORY, str)
        self.assertIsInstance(DEFAULT_SUBCATEGORY, str)
        self.assertIsInstance(DEFAULT_YEAR, str)
        self.assertIsInstance(DEFAULT_MONTH, str)

    def test_urls_are_valid(self):
        """Test that URLs have proper format."""
        self.assertTrue(AR5IV_BASE_URL.startswith('http'))
        self.assertTrue(AR5IV_IMAGE_BASE_URL.startswith('http'))

    def test_numeric_values_positive(self):
        """Test that numeric values are positive."""
        self.assertGreater(MAX_WORKER_THREADS, 0)
        self.assertGreater(TASK_QUEUE_SIZE, 0)
        self.assertGreater(HTML_FETCH_RETRIES, 0)
        self.assertGreater(HTML_FETCH_TIMEOUT, 0)

    def test_default_strings_not_empty(self):
        """Test that default string values are not empty."""
        self.assertTrue(DEFAULT_CATEGORY)
        self.assertTrue(DEFAULT_SUBCATEGORY)
        self.assertTrue(DEFAULT_YEAR)
        self.assertTrue(DEFAULT_MONTH)


if __name__ == '__main__':
    unittest.main()