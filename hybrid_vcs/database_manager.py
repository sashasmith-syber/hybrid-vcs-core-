"""
Database manager for Hybrid VCS state management.
"""

import sqlite3
import logging
from contextlib import contextmanager
from typing import List


class DatabaseManager:
    """Manages SQLite database connections and operations with connection pooling."""
    
    def __init__(self, db_path: str):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn_pool: List[sqlite3.Connection] = []
        self.logger = logging.getLogger(__name__)

    @contextmanager
    def get_connection(self):
        """
        Get a database connection from the pool or create a new one.
        
        Yields:
            sqlite3.Connection: Database connection
        """
        if self.conn_pool:
            conn = self.conn_pool.pop()
            self.logger.debug("Reusing connection from pool")
        else:
            conn = sqlite3.connect(self.db_path, timeout=10)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            self.logger.debug("Created new database connection")
        
        try:
            yield conn
        finally:
            self.conn_pool.append(conn)

    def close_all(self):
        """Close all connections in the pool."""
        for conn in self.conn_pool:
            conn.close()
        self.conn_pool.clear()
        self.logger.info("Closed all database connections")

    def initialize(self):
        """Initialize the database schema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS state (
                    key TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    data BLOB NOT NULL
                );
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    severity INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    params TEXT NOT NULL,
                    commit_hash TEXT
                );
                CREATE TABLE IF NOT EXISTS file_commits (
                    file_hash TEXT PRIMARY KEY,
                    commit_hash TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_file_commits ON file_commits (commit_hash);
                CREATE INDEX IF NOT EXISTS idx_feedback_timestamp ON feedback (timestamp);
                CREATE INDEX IF NOT EXISTS idx_feedback_category ON feedback (category);
            """)
            conn.commit()
            self.logger.info("Database schema initialized")

    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """
        Execute a SELECT query and return results.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of result rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def execute_write(self, query: str, params: tuple = ()) -> None:
        """
        Execute an INSERT/UPDATE/DELETE query.

        Args:
            query: SQL query string
            params: Query parameters
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    def __del__(self):
        """Cleanup when the object is destroyed."""
        self.close_all()
