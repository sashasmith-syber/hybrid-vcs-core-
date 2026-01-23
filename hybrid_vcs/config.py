"""
Configuration settings for Hybrid VCS.
"""

import os

# Default configuration
CONFIG = {
    "REPO_DIR": os.path.abspath(os.getenv("HYBRID_VCS", "./hybrid_repo")),
    "STATE_DB": "state.db",
    "BINARY_DIR": "binaries",
    "ZSTD_LEVEL": 6,
    "MAX_STATE_SIZE": 100 * 1024 * 1024,  # 100MB
    "MAX_WORKERS": 4,  # For parallel compression
}

def get_config():
    """Get the current configuration."""
    return CONFIG.copy()

def update_config(updates: dict):
    """Update configuration with new values."""
    CONFIG.update(updates)

def reset_config():
    """Reset configuration to defaults."""
    global CONFIG
    CONFIG = {
        "REPO_DIR": os.path.abspath(os.getenv("HYBRID_VCS", "./hybrid_repo")),
        "STATE_DB": "state.db",
        "BINARY_DIR": "binaries",
        "ZSTD_LEVEL": 6,
        "MAX_STATE_SIZE": 100 * 1024 * 1024,  # 100MB
        "MAX_WORKERS": 4,  # For parallel compression
    }
