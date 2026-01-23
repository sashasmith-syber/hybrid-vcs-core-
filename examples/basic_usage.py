"""
Basic usage example for Hybrid VCS.
"""

import os
import sys
import logging

# Add parent directory to path to import hybrid_vcs
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hybrid_vcs import HybridVCS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
)

def main():
    """Demonstrate basic Hybrid VCS functionality."""
    print("=== Hybrid VCS Basic Usage Example ===\n")
    
    # Initialize Hybrid VCS
    print("1. Initializing Hybrid VCS...")
    vcs = HybridVCS()
    print(f"   Repository initialized at: {vcs.config['REPO_DIR']}")
    
    # Create a branch
    print("\n2. Creating development branch...")
    try:
        vcs.create_branch("development")
        print("   Created and switched to 'development' branch")
    except Exception as e:
        print(f"   Branch may already exist: {e}")
    
    # Create some example files
    print("\n3. Creating example files...")
    example_files = []
    
    # Create a binary model file
    model_file = "example_model.bin"
    with open(model_file, "wb") as f:
        f.write(os.urandom(1024 * 512))  # 512KB random data
    example_files.append(model_file)
    print(f"   Created {model_file} (512KB)")
    
    # Create a configuration file
    config_file = "model_config.json"
    import json
    config_data = {
        "model_type": "neural_network",
        "layers": [128, 64, 32, 10],
        "learning_rate": 0.001,
        "batch_size": 32,
        "epochs": 100
    }
    with open(config_file, "w") as f:
        json.dump(config_data, f, indent=2)
    example_files.append(config_file)
    print(f"   Created {config_file}")
    
    # Save version
    print("\n4. Saving files to version control...")
    commit_hash = vcs.save_version(example_files, "Initial model and configuration")
    print(f"   Files saved with commit: {commit_hash[:8]}...")
    
    # Save state
    print("\n5. Saving application state...")
    app_state = {
        "last_training_session": "2024-01-15T10:30:00Z",
        "model_version": "1.0.0",
        "performance_metrics": {
            "accuracy": 0.892,
            "loss": 0.523,
            "f1_score": 0.876
        },
        "hyperparameters": config_data
    }
    vcs.save_state("training_session_1", app_state)
    print("   Application state saved")
    
    # Record feedback
    print("\n6. Recording training feedback...")
    vcs.record_feedback(
        severity=7,
        category="training_performance",
        params={
            "final_accuracy": 0.892,
            "training_time_minutes": 45,
            "convergence_epoch": 87,
            "gpu_utilization": 0.95
        },
        commit_hash=commit_hash
    )
    print("   Training feedback recorded")
    
    # Load state
    print("\n7. Loading application state...")
    loaded_state = vcs.load_state("training_session_1")
    if loaded_state:
        print(f"   Loaded state - Model version: {loaded_state['model_version']}")
        print(f"   Performance - Accuracy: {loaded_state['performance_metrics']['accuracy']}")
    
    # Retrieve version
    print("\n8. Retrieving versioned files...")
    try:
        file_data_list = vcs.get_version(commit_hash)
        print(f"   Retrieved {len(file_data_list)} files")
        print(f"   File sizes: {[len(data) for data in file_data_list]} bytes")
    except Exception as e:
        print(f"   Error retrieving files: {e}")
    
    # Show status
    print("\n9. Repository status...")
    status = vcs.get_status()
    print(f"   Current branch: {status['current_branch']}")
    print(f"   Total branches: {len(status['branches'])}")
    print(f"   Recent commits: {len(status['recent_commits'])}")
    
    # Cleanup
    print("\n10. Cleaning up example files...")
    for file_path in example_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"   Removed {file_path}")
    
    vcs.cleanup()
    print("\n=== Example completed successfully! ===")


if __name__ == "__main__":
    main()
