#!/usr/bin/env python3
"""
Quick start script for Hybrid VCS - demonstrates basic functionality.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the hybrid_vcs package to the path
sys.path.insert(0, str(Path(__file__).parent))

from hybrid_vcs import HybridVCS

def main():
    """Quick demonstration of Hybrid VCS capabilities."""
    print("🚀 Hybrid VCS Quick Start Demo")
    print("=" * 50)
    
    # Create a temporary directory for the demo
    demo_dir = tempfile.mkdtemp(prefix="hybrid_vcs_demo_")
    print(f"📁 Demo directory: {demo_dir}")
    
    try:
        # Initialize Hybrid VCS
        print("\n1️⃣ Initializing Hybrid VCS...")
        config = {
            "REPO_DIR": os.path.join(demo_dir, "hybrid_repo"),
            "ZSTD_LEVEL": 6,
            "MAX_WORKERS": 2
        }
        vcs = HybridVCS(config)
        print("✅ Hybrid VCS initialized successfully!")
        
        # Create some demo files
        print("\n2️⃣ Creating demo files...")
        demo_files = []
        
        # Create a text file
        text_file = os.path.join(demo_dir, "demo_config.json")
        with open(text_file, "w") as f:
            f.write('{\n  "model": "demo_model",\n  "version": "1.0",\n  "parameters": {\n    "learning_rate": 0.001,\n    "batch_size": 32\n  }\n}')
        demo_files.append(text_file)
        
        # Create a binary file
        binary_file = os.path.join(demo_dir, "demo_model.bin")
        with open(binary_file, "wb") as f:
            f.write(b"DEMO_MODEL_DATA" * 1000)  # 15KB of demo data
        demo_files.append(binary_file)
        
        print(f"✅ Created {len(demo_files)} demo files")
        
        # Save version
        print("\n3️⃣ Saving files to version control...")
        commit_hash = vcs.save_version(demo_files, "Initial demo version")
        print(f"✅ Files saved with commit: {commit_hash[:8]}...")
        
        # Save application state
        print("\n4️⃣ Saving application state...")
        app_state = {
            "demo_session": "quick_start",
            "timestamp": "2024-01-15T10:00:00Z",
            "metrics": {
                "files_processed": len(demo_files),
                "demo_successful": True
            }
        }
        vcs.save_state("demo_state", app_state)
        print("✅ Application state saved")
        
        # Record feedback
        print("\n5️⃣ Recording feedback...")
        vcs.record_feedback(
            severity=8,
            category="demo_completion",
            params={
                "demo_type": "quick_start",
                "files_count": len(demo_files),
                "success": True
            },
            commit_hash=commit_hash
        )
        print("✅ Feedback recorded")
        
        # Load state back
        print("\n6️⃣ Loading application state...")
        loaded_state = vcs.load_state("demo_state")
        if loaded_state:
            print(f"✅ State loaded - Demo session: {loaded_state['demo_session']}")
            print(f"   Files processed: {loaded_state['metrics']['files_processed']}")
        
        # Show repository status
        print("\n7️⃣ Repository status...")
        status = vcs.get_status()
        print(f"✅ Current branch: {status['current_branch']}")
        print(f"   Repository: {status['repo_dir']}")
        print(f"   Recent commits: {len(status['recent_commits'])}")
        
        # Demonstrate file retrieval
        print("\n8️⃣ Retrieving versioned files...")
        try:
            retrieved_files = vcs.get_version(commit_hash)
            print(f"✅ Retrieved {len(retrieved_files)} files")
            print(f"   File sizes: {[len(data) for data in retrieved_files]} bytes")
        except Exception as e:
            print(f"ℹ️  File retrieval demo skipped: {e}")
        
        print("\n🎉 Quick start demo completed successfully!")
        print("\nNext steps:")
        print("• Run 'python examples/basic_usage.py' for a detailed example")
        print("• Run 'python examples/advanced_usage.py' for advanced features")
        print("• Check the README.md for full documentation")
        print("• Use 'hybrid-vcs --help' for CLI usage")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1
    
    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up demo directory: {demo_dir}")
        try:
            # Clean up demo files
            for file_path in demo_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # Clean up temporary directory
            shutil.rmtree(demo_dir, ignore_errors=True)
            print("✅ Cleanup completed")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
