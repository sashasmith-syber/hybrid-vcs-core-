"""
Tests for the core Hybrid VCS functionality.
"""

import os
import tempfile
import shutil
import json
import pytest
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hybrid_vcs.core import HybridVCS
from hybrid_vcs.config import CONFIG


class TestHybridVCS:
    """Test cases for HybridVCS class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def test_config(self, temp_dir):
        """Create test configuration."""
        config = CONFIG.copy()
        config["REPO_DIR"] = os.path.join(temp_dir, "test_repo")
        return config
    
    @pytest.fixture
    def vcs(self, test_config):
        """Create HybridVCS instance for testing."""
        return HybridVCS(test_config)
    
    @pytest.fixture
    def test_file(self, temp_dir):
        """Create a test file."""
        file_path = os.path.join(temp_dir, "test_file.bin")
        with open(file_path, "wb") as f:
            f.write(b"test data" * 1000)  # 9KB file
        return file_path
    
    def test_initialization(self, vcs, test_config):
        """Test VCS initialization."""
        assert vcs.config == test_config
        assert os.path.exists(test_config["REPO_DIR"])
        assert os.path.exists(os.path.join(test_config["REPO_DIR"], test_config["BINARY_DIR"]))
    
    def test_save_state(self, vcs):
        """Test state saving functionality."""
        test_state = {"key1": "value1", "key2": 42, "key3": [1, 2, 3]}
        vcs.save_state("test_state", test_state)
        
        loaded_state = vcs.load_state("test_state")
        assert loaded_state == test_state
    
    def test_load_nonexistent_state(self, vcs):
        """Test loading non-existent state."""
        result = vcs.load_state("nonexistent")
        assert result is None
    
    def test_invalid_state_key(self, vcs):
        """Test invalid state key validation."""
        with pytest.raises(ValueError, match="Invalid state key"):
            vcs.save_state("invalid-key!", {"data": "test"})
    
    def test_state_size_limit(self, vcs):
        """Test state size limit enforcement."""
        # Create data that exceeds the limit
        large_data = {"data": "x" * (vcs.config["MAX_STATE_SIZE"] + 1)}
        
        with pytest.raises(ValueError, match="State exceeds size limit"):
            vcs.save_state("large_state", large_data)
    
    def test_record_feedback(self, vcs):
        """Test feedback recording."""
        params = {"accuracy": 0.95, "loss": 0.05}
        
        # Should not raise any exceptions
        vcs.record_feedback(5, "training", params, "abc123")
        vcs.record_feedback(8, "validation", params)
    
    def test_invalid_feedback_severity(self, vcs):
        """Test invalid feedback severity."""
        with pytest.raises(ValueError, match="Severity must be 0-10"):
            vcs.record_feedback(15, "test", {})
        
        with pytest.raises(ValueError, match="Severity must be 0-10"):
            vcs.record_feedback(-1, "test", {})
    
    def test_invalid_feedback_category(self, vcs):
        """Test invalid feedback category."""
        long_category = "x" * 65  # Exceeds 64 character limit
        
        with pytest.raises(ValueError, match="Category exceeds 64 characters"):
            vcs.record_feedback(5, long_category, {})
    
    def test_save_version_no_files(self, vcs):
        """Test save_version with no files."""
        with pytest.raises(ValueError, match="No files provided"):
            vcs.save_version([], "test message")
    
    def test_save_version_nonexistent_file(self, vcs):
        """Test save_version with non-existent file."""
        with pytest.raises(FileNotFoundError):
            vcs.save_version(["nonexistent.txt"], "test message")
    
    @patch('hybrid_vcs.core.ProcessPoolExecutor')
    @patch('hybrid_vcs.core.compress_file')
    def test_save_version_success(self, mock_compress, mock_executor, vcs, test_file):
        """Test successful version saving."""
        # Mock the compression process
        mock_future = MagicMock()
        mock_future.result.return_value = "test_hash"
        mock_executor.return_value.__enter__.return_value.submit.return_value = mock_future
        
        # Mock Git operations
        with patch.object(vcs.repo, 'stage') as mock_stage:
            mock_index = MagicMock()
            mock_commit = MagicMock()
            mock_commit.hexsha = "commit_hash_123"
            mock_index.commit.return_value = mock_commit
            mock_stage.return_value.__enter__.return_value = mock_index
            
            commit_hash = vcs.save_version([test_file], "test commit")
            assert commit_hash == "commit_hash_123"
    
    def test_get_status(self, vcs):
        """Test status retrieval."""
        status = vcs.get_status()
        
        assert "current_branch" in status
        assert "branches" in status
        assert "recent_commits" in status
        assert "repo_dir" in status
        assert "config" in status
    
    def test_branch_operations(self, vcs):
        """Test branch creation and switching."""
        # These will be mocked in actual Git operations
        with patch.object(vcs.repo, 'create_branch') as mock_create:
            vcs.create_branch("test_branch")
            mock_create.assert_called_once_with("test_branch")
        
        with patch.object(vcs.repo, 'switch_branch') as mock_switch:
            vcs.switch_branch("test_branch")
            mock_switch.assert_called_once_with("test_branch")
    
    def test_cleanup(self, vcs):
        """Test cleanup functionality."""
        # Should not raise any exceptions
        vcs.cleanup()
    
    def test_context_manager_behavior(self, vcs):
        """Test that VCS can be used as context manager."""
        # The __del__ method should handle cleanup gracefully
        del vcs  # This should not raise any exceptions


class TestHybridVCSIntegration:
    """Integration tests for HybridVCS."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def integration_config(self, temp_dir):
        """Create integration test configuration."""
        config = CONFIG.copy()
        config["REPO_DIR"] = os.path.join(temp_dir, "integration_repo")
        config["MAX_WORKERS"] = 2  # Reduce for testing
        return config
    
    def test_full_workflow(self, integration_config, temp_dir):
        """Test a complete workflow."""
        vcs = HybridVCS(integration_config)
        
        # Create test files
        test_files = []
        for i in range(3):
            file_path = os.path.join(temp_dir, f"test_file_{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"Test content {i}\n" * 100)
            test_files.append(file_path)
        
        # Save state
        test_state = {
            "experiment_id": "test_001",
            "parameters": {"lr": 0.001, "epochs": 10},
            "metrics": {"accuracy": 0.85}
        }
        vcs.save_state("experiment_state", test_state)
        
        # Verify state was saved
        loaded_state = vcs.load_state("experiment_state")
        assert loaded_state == test_state
        
        # Record feedback
        vcs.record_feedback(
            severity=7,
            category="integration_test",
            params={"test_passed": True, "files_count": len(test_files)}
        )
        
        # Get status
        status = vcs.get_status()
        assert status["repo_dir"] == integration_config["REPO_DIR"]
        
        # Cleanup
        vcs.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
