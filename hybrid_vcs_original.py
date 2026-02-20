"""
Hybrid VCS Core Implementation
A version control system combining centralized and distributed features
"""

import os
import json
import hashlib
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class HybridVCS:
    """
    Hybrid Version Control System
    
    Combines centralized repository management with distributed local operations.
    Supports branching, merging, and version tracking for any file type.
    """
    
    def __init__(self, repo_path: str = "./repos", central_server: Optional[str] = None):
        """
        Initialize Hybrid VCS
        
        Args:
            repo_path: Path to store repositories
            central_server: URL of central server (optional for distributed mode)
        """
        self.repo_path = Path(repo_path)
        self.repo_path.mkdir(exist_ok=True)
        self.central_server = central_server
        self.metadata_file = self.repo_path / "metadata.json"
        self._load_metadata()
    
    def _load_metadata(self):
        """Load repository metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {
                "repositories": {},
                "created": datetime.now().isoformat(),
                "version": "1.0.0"
            }
            self._save_metadata()
    
    def _save_metadata(self):
        """Save repository metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _compute_hash(self, data: bytes) -> str:
        """Compute SHA-256 hash of data"""
        return hashlib.sha256(data).hexdigest()
    
    def init_repository(self, repo_name: str) -> Dict[str, Any]:
        """
        Initialize a new repository
        
        Args:
            repo_name: Name of the repository
            
        Returns:
            Dictionary with repository information
        """
        repo_dir = self.repo_path / repo_name
        
        if repo_dir.exists():
            return {"error": f"Repository '{repo_name}' already exists"}
        
        # Create repository structure
        repo_dir.mkdir(parents=True)
        (repo_dir / "objects").mkdir()
        (repo_dir / "refs").mkdir()
        (repo_dir / "refs" / "heads").mkdir()
        (repo_dir / "refs" / "tags").mkdir()
        (repo_dir / "working").mkdir()
        
        # Initialize repository metadata
        repo_meta = {
            "name": repo_name,
            "created": datetime.now().isoformat(),
            "branches": {"main": None},
            "current_branch": "main",
            "commits": [],
            "central_sync": self.central_server is not None
        }
        
        with open(repo_dir / "config.json", 'w') as f:
            json.dump(repo_meta, f, indent=2)
        
        self.metadata["repositories"][repo_name] = {
            "path": str(repo_dir),
            "created": repo_meta["created"]
        }
        self._save_metadata()
        
        return {
            "success": True,
            "repository": repo_name,
            "path": str(repo_dir),
            "message": f"Initialized empty Hybrid VCS repository in {repo_dir}"
        }
    
    def add_file(self, repo_name: str, file_path: str, content: bytes) -> Dict[str, Any]:
        """
        Add a file to the repository staging area
        
        Args:
            repo_name: Repository name
            file_path: Path within repository
            content: File content
            
        Returns:
            Dictionary with operation result
        """
        repo_dir = self.repo_path / repo_name
        
        if not repo_dir.exists():
            return {"error": f"Repository '{repo_name}' does not exist"}
        
        # Compute content hash
        content_hash = self._compute_hash(content)
        
        # Store object
        object_path = repo_dir / "objects" / content_hash
        with open(object_path, 'wb') as f:
            f.write(content)
        
        # Update staging area
        staging_file = repo_dir / "staging.json"
        if staging_file.exists():
            with open(staging_file, 'r') as f:
                staging = json.load(f)
        else:
            staging = {}
        
        staging[file_path] = {
            "hash": content_hash,
            "size": len(content),
            "timestamp": datetime.now().isoformat()
        }
        
        with open(staging_file, 'w') as f:
            json.dump(staging, f, indent=2)
        
        return {
            "success": True,
            "file": file_path,
            "hash": content_hash,
            "size": len(content)
        }
    
    def commit(self, repo_name: str, message: str, author: str = "Unknown") -> Dict[str, Any]:
        """
        Commit staged changes
        
        Args:
            repo_name: Repository name
            message: Commit message
            author: Commit author
            
        Returns:
            Dictionary with commit information
        """
        repo_dir = self.repo_path / repo_name
        
        if not repo_dir.exists():
            return {"error": f"Repository '{repo_name}' does not exist"}
        
        staging_file = repo_dir / "staging.json"
        if not staging_file.exists():
            return {"error": "No changes staged for commit"}
        
        with open(staging_file, 'r') as f:
            staging = json.load(f)
        
        if not staging:
            return {"error": "No changes staged for commit"}
        
        # Load repository config
        with open(repo_dir / "config.json", 'r') as f:
            config = json.load(f)
        
        # Create commit object
        commit_id = self._compute_hash(
            (message + author + str(time.time())).encode()
        )
        
        commit_obj = {
            "id": commit_id,
            "message": message,
            "author": author,
            "timestamp": datetime.now().isoformat(),
            "files": staging,
            "parent": config["branches"][config["current_branch"]],
            "branch": config["current_branch"]
        }
        
        # Save commit
        commit_path = repo_dir / "objects" / f"commit_{commit_id}.json"
        with open(commit_path, 'w') as f:
            json.dump(commit_obj, f, indent=2)
        
        # Update branch pointer
        config["branches"][config["current_branch"]] = commit_id
        config["commits"].append(commit_id)
        
        with open(repo_dir / "config.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        # Clear staging
        staging_file.unlink()
        
        return {
            "success": True,
            "commit_id": commit_id,
            "message": message,
            "files": len(staging),
            "branch": config["current_branch"]
        }
    
    def get_history(self, repo_name: str, limit: int = 10) -> Dict[str, Any]:
        """
        Get commit history
        
        Args:
            repo_name: Repository name
            limit: Maximum number of commits to return
            
        Returns:
            Dictionary with commit history
        """
        repo_dir = self.repo_path / repo_name
        
        if not repo_dir.exists():
            return {"error": f"Repository '{repo_name}' does not exist"}
        
        with open(repo_dir / "config.json", 'r') as f:
            config = json.load(f)
        
        commits = []
        for commit_id in reversed(config["commits"][-limit:]):
            commit_path = repo_dir / "objects" / f"commit_{commit_id}.json"
            if commit_path.exists():
                with open(commit_path, 'r') as f:
                    commits.append(json.load(f))
        
        return {
            "repository": repo_name,
            "commits": commits,
            "total": len(config["commits"])
        }
    
    def create_branch(self, repo_name: str, branch_name: str) -> Dict[str, Any]:
        """
        Create a new branch
        
        Args:
            repo_name: Repository name
            branch_name: New branch name
            
        Returns:
            Dictionary with operation result
        """
        repo_dir = self.repo_path / repo_name
        
        if not repo_dir.exists():
            return {"error": f"Repository '{repo_name}' does not exist"}
        
        with open(repo_dir / "config.json", 'r') as f:
            config = json.load(f)
        
        if branch_name in config["branches"]:
            return {"error": f"Branch '{branch_name}' already exists"}
        
        # Create branch from current HEAD
        current_commit = config["branches"][config["current_branch"]]
        config["branches"][branch_name] = current_commit
        
        with open(repo_dir / "config.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        return {
            "success": True,
            "branch": branch_name,
            "commit": current_commit
        }
    
    def checkout(self, repo_name: str, branch_name: str) -> Dict[str, Any]:
        """
        Switch to a different branch
        
        Args:
            repo_name: Repository name
            branch_name: Branch to switch to
            
        Returns:
            Dictionary with operation result
        """
        repo_dir = self.repo_path / repo_name
        
        if not repo_dir.exists():
            return {"error": f"Repository '{repo_name}' does not exist"}
        
        with open(repo_dir / "config.json", 'r') as f:
            config = json.load(f)
        
        if branch_name not in config["branches"]:
            return {"error": f"Branch '{branch_name}' does not exist"}
        
        config["current_branch"] = branch_name
        
        with open(repo_dir / "config.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        return {
            "success": True,
            "branch": branch_name,
            "commit": config["branches"][branch_name]
        }
    
    def list_repositories(self) -> List[Dict[str, Any]]:
        """List all repositories"""
        repos = []
        for repo_name, repo_info in self.metadata["repositories"].items():
            repo_dir = Path(repo_info["path"])
            if repo_dir.exists():
                with open(repo_dir / "config.json", 'r') as f:
                    config = json.load(f)
                repos.append({
                    "name": repo_name,
                    "created": repo_info["created"],
                    "branches": list(config["branches"].keys()),
                    "commits": len(config["commits"])
                })
        return repos
    
    def get_status(self, repo_name: str) -> Dict[str, Any]:
        """Get repository status"""
        repo_dir = self.repo_path / repo_name
        
        if not repo_dir.exists():
            return {"error": f"Repository '{repo_name}' does not exist"}
        
        with open(repo_dir / "config.json", 'r') as f:
            config = json.load(f)
        
        staging_file = repo_dir / "staging.json"
        staged_files = []
        if staging_file.exists():
            with open(staging_file, 'r') as f:
                staging = json.load(f)
                staged_files = list(staging.keys())
        
        return {
            "repository": repo_name,
            "current_branch": config["current_branch"],
            "branches": config["branches"],
            "total_commits": len(config["commits"]),
            "staged_files": staged_files
        }


def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python hybrid_vcs_original.py <command> [args]")
        print("Commands: init, add, commit, log, branch, checkout, status, list")
        return
    
    command = sys.argv[1]
    vcs = HybridVCS()
    
    if command == "init" and len(sys.argv) >= 3:
        result = vcs.init_repository(sys.argv[2])
        print(json.dumps(result, indent=2))
    elif command == "list":
        repos = vcs.list_repositories()
        print(json.dumps(repos, indent=2))
    elif command == "status" and len(sys.argv) >= 3:
        result = vcs.get_status(sys.argv[2])
        print(json.dumps(result, indent=2))
    else:
        print(f"Unknown or incomplete command: {command}")


if __name__ == "__main__":
    main()
