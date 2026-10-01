"""Unit tests for the logger module."""

import unittest
import logging
from unittest.mock import patch, MagicMock
from src.logger import setup_logger


class TestLogger(unittest.TestCase):
    """Test suite for logger module."""

    def test_setup_logger_basic(self):
        """Test basic logger setup."""
        # Clear any existing handlers to avoid duplicates
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Set up the logger
        setup_logger()
        
        # Verify logger is configured
        self.assertEqual(root_logger.level, logging.INFO)
        
        # Check that handlers are added
        self.assertGreaterEqual(len(root_logger.handlers), 1)
        
        # Check the format of the first handler
        handler = root_logger.handlers[0]
        if hasattr(handler, 'formatter'):
            self.assertIsNotNone(handler.formatter)
            self.assertIn('levelname', handler.formatter._fmt)
            self.assertIn('asctime', handler.formatter._fmt)
            self.assertIn('message', handler.formatter._fmt)


if __name__ == '__main__':
    unittest.main()