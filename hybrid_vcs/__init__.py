"""
Hybrid VCS - A version control system combining Git with SQLite for state management.

This package provides a hybrid approach to version control that combines:
- Git for traditional version control
- SQLite for state and configuration management
- Zstandard compression for binary files
- Parallel processing for performance
"""

from .core import HybridVCS
from .git_manager import GitManager
from .database_manager import DatabaseManager
from .web_server import VCSWebServer, create_server
from .config import CONFIG

__version__ = "1.0.0"
__author__ = "Hybrid VCS Team"
__email__ = "contact@hybridvcs.com"

__all__ = [
    "HybridVCS",
    "GitManager",
    "DatabaseManager",
    "VCSWebServer",
    "create_server",
    "CONFIG"
]
