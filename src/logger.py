# src/logger.py
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import logging
from typing import Optional

def setup_logger():
     """Sets up the logging configuration."""
     logging.basicConfig(
         level=logging.INFO,
         format='%(asctime)s %(levelname)s %(message)s',
         handlers=[logging.StreamHandler()]
     )