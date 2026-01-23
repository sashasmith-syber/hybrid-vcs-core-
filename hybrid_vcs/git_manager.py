"""
Git manager for Hybrid VCS Git operations.
"""

import os
import logging
from contextlib import contextmanager
from git import Repo
from typing import Generator


class GitManager:
    """Manages Git operations with LFS support."""
    
    def __init__(self, repo_dir: str):
        """
        Initialize the Git manager.
        
        Args:
            repo_dir: Path to the Git repository directory
        """
        self.repo_dir = repo_dir
        self.logger = logging.getLogger(__name__)
        
        if not os.path.exists(os.path.join(repo_dir, ".git")):
            self.repo = Repo.init(repo_dir, bare=False)
            self._setup_lfs()
            self.logger.info(f"Initialized new Git repository at {repo_dir}")
        else:
            self.repo = Repo(repo_dir)
            self.logger.info(f"Opened existing Git repository at {repo_dir}")

    def _setup_lfs(self):
        """Set up Git LFS for binary file handling."""
        gitattributes_path = os.path.join(self.repo_dir, ".gitattributes")
        
        # Check if LFS is already configured
        lfs_configured = False
        if os.path.exists(gitattributes_path):
            with open(gitattributes_path, "r") as f:
                content = f.read()
                if "*.zst filter=lfs" in content:
                    lfs_configured = True
        
        if not lfs_configured:
            with open(gitattributes_path, "a") as f:
                f.write("*.zst filter=lfs diff=lfs merge=lfs -text\n")
            
            try:
                self.repo.git.execute(["git", "lfs", "install"])
                self.logger.info("Git LFS configured successfully")
            except Exception as e:
                self.logger.warning(f"Failed to configure Git LFS: {e}")

    @contextmanager
    def stage(self) -> Generator:
        """
        Context manager for staging operations.
        
        Yields:
            Git index for staging operations
        """
        try:
            yield self.repo.index
        finally:
            self.repo.git.clear_cache()

    def create_branch(self, branch_name: str):
        """
        Create a new Git branch.
        
        Args:
            branch_name: Name of the branch to create
        """
        try:
            self.repo.git.checkout("-b", branch_name)
            self.logger.info(f"Created and switched to branch: {branch_name}")
        except Exception as e:
            self.logger.error(f"Failed to create branch {branch_name}: {e}")
            raise

    def switch_branch(self, branch_name: str):
        """
        Switch to an existing Git branch.
        
        Args:
            branch_name: Name of the branch to switch to
        """
        try:
            self.repo.git.checkout(branch_name)
            self.logger.info(f"Switched to branch: {branch_name}")
        except Exception as e:
            self.logger.error(f"Failed to switch to branch {branch_name}: {e}")
            raise

    def get_current_branch(self) -> str:
        """
        Get the name of the current branch.
        
        Returns:
            Name of the current branch
        """
        return self.repo.active_branch.name

    def list_branches(self) -> list:
        """
        List all branches in the repository.
        
        Returns:
            List of branch names
        """
        return [branch.name for branch in self.repo.branches]

    def get_commit_history(self, max_count: int = 10) -> list:
        """
        Get commit history.
        
        Args:
            max_count: Maximum number of commits to retrieve
            
        Returns:
            List of commit information dictionaries
        """
        commits = []
        for commit in self.repo.iter_commits(max_count=max_count):
            commits.append({
                'hash': commit.hexsha,
                'message': commit.message.strip(),
                'author': str(commit.author),
                'date': commit.committed_datetime.isoformat()
            })
        return commits
