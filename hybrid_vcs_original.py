import os
import git
import zstandard
import logging
import hashlib
import json
import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List
from git import Repo
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
import shutil
from contextlib import contextmanager

# Configuration
CONFIG = {
    "REPO_DIR": os.path.abspath(os.getenv("HYBRID_VCS", "./hybrid_repo")),
    "STATE_DB": "state.db",
    "BINARY_DIR": "binaries",
    "ZSTD_LEVEL": 6,
    "MAX_STATE_SIZE": 100 * 1024 * 1024,  # 100MB
    "MAX_WORKERS": 4,  # For parallel compression
}
os.makedirs(CONFIG["REPO_DIR"], mode=0o700, exist_ok=True)
os.makedirs(os.path.join(CONFIG["REPO_DIR"], CONFIG["BINARY_DIR"]), mode=0o700, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
)

# Compress file in a separate process
def compress_file(file_path: str, output_path: str, level: int) -> str:
    with open(file_path, "rb") as f:
        data = f.read()
    content_hash = hashlib.sha256(data).hexdigest()
    with open(output_path, "wb") as f:
        f.write(zstandard.ZstdCompressor(level=level).compress(data))
    return content_hash

# Database Manager with Connection Pooling
class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn_pool = []

    @contextmanager
    def get_connection(self):
        if self.conn_pool:
            conn = self.conn_pool.pop()
        else:
            conn = sqlite3.connect(self.db_path, timeout=10)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
        try:
            yield conn
        finally:
            self.conn_pool.append(conn)

    def close_all(self):
        for conn in self.conn_pool:
            conn.close()
        self.conn_pool.clear()

    def initialize(self):
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
            """)
            conn.commit()

# Git Manager with LFS Support
class GitManager:
    def __init__(self, repo_dir: str):
        self.repo_dir = repo_dir
        if not os.path.exists(os.path.join(repo_dir, ".git")):
            self.repo = Repo.init(repo_dir, bare=False)
            self._setup_lfs()
        else:
            self.repo = Repo(repo_dir)

    def _setup_lfs(self):
        with open(os.path.join(self.repo_dir, ".gitattributes"), "a") as f:
            f.write("*.zst filter=lfs diff=lfs merge=lfs -text\n")
        self.repo.git.execute(["git", "lfs", "install"])

    @contextmanager
    def stage(self):
        try:
            yield self.repo.index
        finally:
            self.repo.git.clear_cache()

    def create_branch(self, branch_name: str):
        self.repo.git.checkout("-b", branch_name)

    def switch_branch(self, branch_name: str):
        self.repo.git.checkout(branch_name)

# Hybrid VCS
class HybridVCS:
    def __init__(self, config: Dict[str, Any] = CONFIG):
        self.config = config
        self.repo = GitManager(config["REPO_DIR"])
        self.db = DatabaseManager(os.path.join(config["REPO_DIR"], config["STATE_DB"]))
        self.db.initialize()
        self.compressor = zstandard.ZstdCompressor(level=config["ZSTD_LEVEL"])
        self.decompressor = zstandard.ZstdDecompressor()

    def save_version(self, file_paths: List[str], message: str) -> str:
        """Save multiple files with Git and compress binaries in parallel"""
        if not file_paths:
            raise ValueError("No files provided")
        
        results = []
        with ProcessPoolExecutor(max_workers=self.config["MAX_WORKERS"]) as executor:
            futures = []
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File {file_path} does not exist")
                if os.path.getsize(file_path) > self.config["MAX_STATE_SIZE"]:
                    raise ValueError(f"File {file_path} exceeds size limit")
                file_hash = hashlib.sha256(open(file_path, "rb").read()).hexdigest()
                output_path = os.path.join(
                    self.config["REPO_DIR"], 
                    self.config["BINARY_DIR"], 
                    f"{file_hash[:2]}/{file_hash}.zst"
                )
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                futures.append(executor.submit(compress_file, file_path, output_path, self.config["ZSTD_LEVEL"]))
            
            for future, file_path in zip(futures, file_paths):
                content_hash = future.result()
                results.append((file_path, content_hash))

        with self.repo.stage() as index:
            for _, content_hash in results:
                index.add([os.path.join(self.config["BINARY_DIR"], f"{content_hash[:2]}/{content_hash}.zst")])
            commit = index.commit(message)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            for _, content_hash in results:
                cursor.execute(
                    "INSERT OR REPLACE INTO file_commits (file_hash, commit_hash) VALUES (?, ?)",
                    (content_hash, commit.hexsha)
                )
            conn.commit()

        return commit.hexsha

    def save_state(self, key: str, value: Dict[str, Any]):
        """Save configuration state in SQLite"""
        if not key.isalnum():
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

    @lru_cache(maxsize=128)
    def load_state(self, key: str) -> Optional[Dict[str, Any]]:
        """Load state from SQLite with caching"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            result = cursor.execute("SELECT data FROM state WHERE key = ?", (key,)).fetchone()
            return json.loads(result[0].decode()) if result else None

    def record_feedback(self, severity: int, category: str, params: Dict[str, Any], commit_hash: Optional[str] = None):
        """Record telemetry linked to Git commit"""
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

    @lru_cache(maxsize=128)
    def get_version(self, commit_hash: str) -> List[bytes]:
        """Retrieve and decompress versioned files for a commit"""
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
                results.append(self.decompressor.decompress(blob.data_stream.read()))
            except Exception as e:
                logging.error(f"Error retrieving and decompressing file {blob_path} for commit {commit_hash}: {e}")
                continue
        return results

    def create_branch(self, branch_name: str):
        """Create a new Git branch"""
        self.repo.create_branch(branch_name)

    def switch_branch(self, branch_name: str):
        """Switch to an existing Git branch"""
        self.repo.switch_branch(branch_name)

    def __del__(self):
        self.db.close_all()

# Example Usage
if __name__ == "__main__":
    vcs = HybridVCS()
    
    # Create a branch
    vcs.create_branch("dev")
    
    # Version multiple binary model files
    with open("model1.bin", "wb") as f:
        f.write(os.urandom(1024 * 1024))  # Dummy 1MB file
    with open("model2.bin", "wb") as f:
        f.write(os.urandom(512 * 1024))  # Dummy 512KB file
    commit_hash = vcs.save_version(["model1.bin", "model2.bin"], "Initial model versions")
    
    # Save configuration state
    vcs.save_state("model_config", {"learning_rate": 0.001, "epochs": 100})
    
    # Record feedback
    vcs.record_feedback(
        severity=8,
        category="training",
        params={"loss": 0.523, "accuracy": 0.892},
        commit_hash=commit_hash
    )
    
    # Retrieve state and versions
    state = vcs.load_state("model_config")
    data_list = vcs.get_version(commit_hash)
    
    logging.info(f"State: {state}")
    logging.info(f"Versions retrieved, count: {len(data_list)}, sizes: {[len(data) for data in data_list]} bytes")
    logging.info("Hybrid VCS initialized. Ready for action!")
