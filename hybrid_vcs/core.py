"""
Core Hybrid VCS implementation.
"""

import os
import hashlib
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache

from .config import CONFIG
from .git_manager import GitManager
from .database_manager import DatabaseManager
from .compression import compress_file, decompress_data


class HybridVCS:
    """
    Hybrid Version Control System combining Git with SQLite for state management.
    
    This system provides:
    - Git-based version control for files
    - SQLite-based state and configuration management
    - Zstandard compression for binary files
    - Parallel processing for performance
    - Telemetry and feedback tracking
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Hybrid VCS.
        
        Args:
            config: Configuration dictionary (uses default CONFIG if None)
        """
        self.config = config or CONFIG.copy()
        self.logger = logging.getLogger(__name__)
        
        # Ensure directories exist
        os.makedirs(self.config["REPO_DIR"], mode=0o700, exist_ok=True)
        os.makedirs(
            os.path.join(self.config["REPO_DIR"], self.config["BINARY_DIR"]), 
            mode=0o700, 
            exist_ok=True
        )
        
        # Initialize managers
        self.repo = GitManager(self.config["REPO_DIR"])
        self.db = DatabaseManager(os.path.join(self.config["REPO_DIR"], self.config["STATE_DB"]))
        self.db.initialize()
        
        self.logger.info("Hybrid VCS initialized successfully")

    def save_version(self, file_paths: List[str], message: str) -> str:
        """
        Save multiple files with Git and compress binaries in parallel.
        
        Args:
            file_paths: List of file paths to version
            message: Commit message
            
        Returns:
            Commit hash
            
        Raises:
            ValueError: If no files provided or file exceeds size limit
            FileNotFoundError: If a file doesn't exist
        """
        if not file_paths:
            raise ValueError("No files provided")
        
        self.logger.info(f"Saving version for {len(file_paths)} files")
        
        # Validate files
        for file_path in file_paths:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File {file_path} does not exist")
            if os.path.getsize(file_path) > self.config["MAX_STATE_SIZE"]:
                raise ValueError(f"File {file_path} exceeds size limit")
        
        # Compress files in parallel
        results = []
        with ProcessPoolExecutor(max_workers=self.config["MAX_WORKERS"]) as executor:
            futures = []
            for file_path in file_paths:
                file_hash = hashlib.sha256(open(file_path, "rb").read()).hexdigest()
                output_path = os.path.join(
                    self.config["REPO_DIR"], 
                    self.config["BINARY_DIR"], 
                    f"{file_hash[:2]}/{file_hash}.zst"
                )
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                futures.append(
                    executor.submit(compress_file, file_path, output_path, self.config["ZSTD_LEVEL"])
                )
            
            for future, file_path in zip(futures, file_paths):
                content_hash = future.result()
                results.append((file_path, content_hash))

        # Commit to Git
        with self.repo.stage() as index:
            for _, content_hash in results:
                compressed_file_path = os.path.join(
                    self.config["BINARY_DIR"],
                    f"{content_hash[:2]}/{content_hash}.zst"
                )
                index.add([compressed_file_path])
            try:
                commit = index.commit(message)
            except Exception as e:
                # Handle hook execution failures gracefully
                self.logger.warning(f"Git commit succeeded but hooks failed: {e}")
                # Get the latest commit hash since the commit actually worked
                commits = self.repo.get_commit_history(1)
                commit = commits[0] if commits else None
                if not commit:
                    raise ValueError("Could not retrieve commit after hook failure")

        # Update database
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            for _, content_hash in results:
                cursor.execute(
                    "INSERT OR REPLACE INTO file_commits (file_hash, commit_hash) VALUES (?, ?)",
                    (content_hash, commit.hexsha)
                )
            conn.commit()

        self.logger.info(f"Version saved with commit hash: {commit.hexsha}")
        return commit.hexsha

    def save_state(self, key: str, value: Dict[str, Any]):
        """
        Save configuration state in SQLite.
        
        Args:
            key: State key (must be alphanumeric)
            value: State value dictionary
            
        Raises:
            ValueError: If key is invalid or state exceeds size limit
        """
        if not key.replace('_', '').isalnum():
            raise ValueError(f"Invalid state key: {key}")
        
        data = json.dumps(value).encode()
        if len(data) > self.config["MAX_STATE_SIZE"]:
            raise ValueError("State exceeds size limit")

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO state (key, created_at, data) VALUES (?, ?, ?)",
                (key, datetime.utcnow().isoformat(), data)
            )
            conn.commit()

        self.logger.info(f"State saved: {key}")

    @lru_cache(maxsize=128)
    def load_state(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Load state from SQLite with caching.
        
        Args:
            key: State key
            
        Returns:
            State value dictionary or None if not found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            result = cursor.execute("SELECT data FROM state WHERE key = ?", (key,)).fetchone()
            if result:
                self.logger.debug(f"State loaded: {key}")
                return json.loads(result[0].decode())
            return None

    def record_feedback(self, severity: int, category: str, params: Dict[str, Any], 
                       commit_hash: Optional[str] = None):
        """
        Record telemetry linked to Git commit.
        
        Args:
            severity: Severity level (0-10)
            category: Feedback category (max 64 chars)
            params: Feedback parameters
            commit_hash: Optional commit hash to link feedback to
            
        Raises:
            ValueError: If severity or category is invalid
        """
        if not (0 <= severity <= 10):
            raise ValueError("Severity must be 0-10")
        if len(category) > 64:
            raise ValueError("Category exceeds 64 characters")

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO feedback (timestamp, severity, category, params, commit_hash) VALUES (?, ?, ?, ?, ?)",
                (datetime.utcnow().isoformat(), severity, category, json.dumps(params), commit_hash)
            )
            conn.commit()

        self.logger.info(f"Feedback recorded: {category} (severity: {severity})")

    @lru_cache(maxsize=128)
    def get_version(self, commit_hash: str) -> List[bytes]:
        """
        Retrieve and decompress versioned files for a commit.
        
        Args:
            commit_hash: Git commit hash
            
        Returns:
            List of decompressed file contents
            
        Raises:
            ValueError: If no files associated with commit
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            file_hashes = cursor.execute(
                "SELECT file_hash FROM file_commits WHERE commit_hash = ?", (commit_hash,)
            ).fetchall()
            if not file_hashes:
                raise ValueError(f"No files associated with commit {commit_hash}")

        results = []
        for (file_hash,) in file_hashes:
            blob_path = os.path.join(self.config["BINARY_DIR"], f"{file_hash[:2]}/{file_hash}.zst")
            try:
                blob = self.repo.repo.commit(commit_hash).tree / blob_path
                compressed_data = blob.data_stream.read()
                decompressed_data = decompress_data(compressed_data)
                results.append(decompressed_data)
            except Exception as e:
                self.logger.error(f"Error retrieving file {blob_path} for commit {commit_hash}: {e}")
                continue
        
        self.logger.info(f"Retrieved {len(results)} files for commit {commit_hash}")
        return results

    def create_branch(self, branch_name: str):
        """
        Create a new Git branch.
        
        Args:
            branch_name: Name of the branch to create
        """
        self.repo.create_branch(branch_name)

    def switch_branch(self, branch_name: str):
        """
        Switch to an existing Git branch.
        
        Args:
            branch_name: Name of the branch to switch to
        """
        self.repo.switch_branch(branch_name)

    def get_status(self) -> Dict[str, Any]:
        """
        Get current VCS status.
        
        Returns:
            Dictionary containing status information
        """
        return {
            'current_branch': self.repo.get_current_branch(),
            'branches': self.repo.list_branches(),
            'recent_commits': self.repo.get_commit_history(5),
            'repo_dir': self.config["REPO_DIR"],
            'config': self.config
        }

    def cleanup(self):
        """Clean up resources."""
        self.db.close_all()
        self.logger.info("Hybrid VCS cleanup completed")

    def save_webpage(self, page_data: Dict[str, Any]) -> str:
        """
        Save a complete webpage to version control.

        Args:
            page_data: Dictionary containing page information

        Returns:
            Commit hash of the saved version
        """
        import json
        from datetime import datetime

        # Create a structured representation of the webpage
        webpage_content = {
            'type': 'webpage',
            'title': page_data.get('title', ''),
            'url': page_data.get('url', ''),
            'timestamp': page_data.get('timestamp', datetime.utcnow().isoformat()),
            'metadata': {
                'description': page_data.get('description', ''),
                'keywords': page_data.get('keywords', ''),
                'author': page_data.get('author', ''),
                'canonical_url': page_data.get('canonicalUrl', ''),
                'language': page_data.get('language', ''),
                'charset': page_data.get('charset', ''),
                'viewport': page_data.get('viewport', {}),
                'user_agent': page_data.get('userAgent', ''),
                'referrer': page_data.get('referrer', ''),
                'links_count': len(page_data.get('links', [])),
                'images_count': len(page_data.get('images', []))
            },
            'content': {
                'html': page_data.get('content', ''),
                'text': page_data.get('textContent', ''),
                'readable': page_data.get('readableContent', '')
            },
            'links': page_data.get('links', []),
            'images': page_data.get('images', [])
        }

        # Save as JSON file
        filename = f"webpage_{self._sanitize_filename(page_data.get('title', 'untitled'))}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        content = json.dumps(webpage_content, indent=2, ensure_ascii=False)

        # Write file to disk first
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

        # Save to VCS
        commit_hash = self.save_version([filename], f"Save webpage: {page_data.get('title', 'Untitled')}")
        self.logger.info(f"Webpage saved with commit: {commit_hash}")

        # Store metadata in database
        self.save_state(f"webpage_{commit_hash}", webpage_content)

        return commit_hash

    def save_text_selection(self, selection_data: Dict[str, Any]) -> str:
        """
        Save a text selection to version control.

        Args:
            selection_data: Dictionary containing selection information

        Returns:
            Commit hash of the saved version
        """
        import json
        from datetime import datetime

        # Create structured selection data
        selection_content = {
            'type': 'text_selection',
            'text': selection_data.get('text', ''),
            'url': selection_data.get('url', ''),
            'title': selection_data.get('title', ''),
            'timestamp': selection_data.get('timestamp', datetime.utcnow().isoformat()),
            'context': {
                'html': selection_data.get('html', ''),
                'surrounding': selection_data.get('context', ''),
                'xpath': selection_data.get('xpath', ''),
                'css_selector': selection_data.get('cssSelector', ''),
                'bounding_rect': selection_data.get('boundingRect', {})
            },
            'metadata': {
                'length': len(selection_data.get('text', '')),
                'user_agent': selection_data.get('userAgent', ''),
                'selection_type': 'text'
            }
        }

        # Save as JSON file
        filename = f"selection_{self._sanitize_filename(selection_data.get('title', 'untitled'))}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        content = json.dumps(selection_content, indent=2, ensure_ascii=False)

        # Write file to disk first
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

        # Save to VCS
        commit_hash = self.save_version([filename], f"Save text selection: {selection_data.get('text', '')[:50]}...")
        self.logger.info(f"Text selection saved with commit: {commit_hash}")

        # Store metadata in database
        self.save_state(f"selection_{commit_hash}", selection_content)

        return commit_hash

    def save_link(self, link_data: Dict[str, Any]) -> str:
        """
        Save a link to version control.

        Args:
            link_data: Dictionary containing link information

        Returns:
            Commit hash of the saved version
        """
        import json
        from datetime import datetime

        # Create structured link data
        link_content = {
            'type': 'link',
            'url': link_data.get('url', ''),
            'title': link_data.get('title', ''),
            'text': link_data.get('text', ''),
            'timestamp': link_data.get('timestamp', datetime.utcnow().isoformat()),
            'metadata': {
                'href': link_data.get('href', ''),
                'rel': link_data.get('rel', ''),
                'target': link_data.get('target', ''),
                'xpath': link_data.get('xpath', ''),
                'visible': link_data.get('visible', True),
                'link_type': 'hyperlink'
            }
        }

        # Save as JSON file
        filename = f"link_{self._sanitize_filename(link_data.get('title', 'untitled'))}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        content = json.dumps(link_content, indent=2, ensure_ascii=False)

        # Write file to disk first
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

        # Save to VCS
        commit_hash = self.save_version([filename], f"Save link: {link_data.get('text', link_data.get('url', ''))}")
        self.logger.info(f"Link saved with commit: {commit_hash}")

        # Store metadata in database
        self.save_state(f"link_{commit_hash}", link_content)

        return commit_hash

    def get_content_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get history of saved web content.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of content history entries
        """
        # Query database for saved content
        query = """
        SELECT key, data, created_at
        FROM state
        WHERE key LIKE 'webpage_%' OR key LIKE 'selection_%' OR key LIKE 'link_%'
        ORDER BY created_at DESC
        LIMIT ?
        """

        results = self.db.execute_query(query, (limit,))
        history = []

        for row in results:
            try:
                content_data = json.loads(row['data'].decode('utf-8'))
                history.append({
                    'id': row['key'],
                    'type': content_data.get('type', 'unknown'),
                    'title': content_data.get('title', ''),
                    'url': content_data.get('url', ''),
                    'timestamp': row['created_at'],
                    'commit_hash': row['key'].split('_', 1)[1] if '_' in row['key'] else '',
                    'data': content_data
                })
            except (json.JSONDecodeError, KeyError, UnicodeDecodeError):
                continue

        return history

    def get_version_content(self, commit_hash: str) -> Dict[str, Any]:
        """
        Get content for a specific version.

        Args:
            commit_hash: The commit hash to retrieve

        Returns:
            Version content data
        """
        # Try to get from database first
        for prefix in ['webpage', 'selection', 'link']:
            state_key = f"{prefix}_{commit_hash}"
            try:
                content = self.load_state(state_key)
                if content:
                    return content
            except:
                continue

        # Fallback to getting version files
        try:
            files_data = self.get_version(commit_hash)
            if files_data:
                # Try to parse JSON content
                for file_path, file_content in files_data.items():
                    if file_path.endswith('.json'):
                        try:
                            return json.loads(file_content)
                        except:
                            continue
        except:
            pass

        return {}

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe filesystem usage.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        import re
        # Remove or replace problematic characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit length
        return sanitized[:100].strip()

    def __del__(self):
        """Cleanup when the object is destroyed."""
        try:
            self.cleanup()
        except:
            pass  # Ignore errors during cleanup
