"""
Advanced usage example for Hybrid VCS demonstrating parallel processing and branching.
"""

import os
import sys
import json
import time
import logging
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path to import hybrid_vcs
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hybrid_vcs import HybridVCS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
)

def create_model_checkpoint(model_name: str, size_mb: int = 1) -> str:
    """Create a dummy model checkpoint file."""
    filename = f"{model_name}_checkpoint.bin"
    with open(filename, "wb") as f:
        f.write(os.urandom(size_mb * 1024 * 1024))
    return filename

def simulate_training_experiment(vcs: HybridVCS, experiment_id: str, config: dict):
    """Simulate a training experiment with multiple checkpoints."""
    print(f"   Starting experiment: {experiment_id}")
    
    # Create branch for this experiment
    branch_name = f"experiment_{experiment_id}"
    try:
        vcs.create_branch(branch_name)
    except:
        vcs.switch_branch(branch_name)
    
    checkpoints = []
    
    # Create multiple checkpoints
    for epoch in [10, 25, 50, 75, 100]:
        checkpoint_file = create_model_checkpoint(f"{experiment_id}_epoch_{epoch}", size_mb=2)
        checkpoints.append(checkpoint_file)
        
        # Save checkpoint
        commit_hash = vcs.save_version([checkpoint_file], f"Checkpoint at epoch {epoch}")
        
        # Save training state
        training_state = {
            "experiment_id": experiment_id,
            "epoch": epoch,
            "config": config,
            "metrics": {
                "loss": max(0.1, 2.0 - (epoch * 0.015)),  # Simulated decreasing loss
                "accuracy": min(0.95, 0.3 + (epoch * 0.006)),  # Simulated increasing accuracy
                "learning_rate": config["learning_rate"] * (0.95 ** (epoch // 10))
            },
            "timestamp": time.time()
        }
        vcs.save_state(f"{experiment_id}_epoch_{epoch}", training_state)
        
        # Record feedback
        vcs.record_feedback(
            severity=5 if epoch < 50 else 8,
            category="training_checkpoint",
            params={
                "epoch": epoch,
                "experiment_id": experiment_id,
                "loss": training_state["metrics"]["loss"],
                "accuracy": training_state["metrics"]["accuracy"]
            },
            commit_hash=commit_hash
        )
    
    # Cleanup checkpoint files
    for checkpoint in checkpoints:
        if os.path.exists(checkpoint):
            os.remove(checkpoint)
    
    print(f"   Completed experiment: {experiment_id}")
    return experiment_id

def main():
    """Demonstrate advanced Hybrid VCS functionality."""
    print("=== Hybrid VCS Advanced Usage Example ===\n")
    
    # Initialize Hybrid VCS
    print("1. Initializing Hybrid VCS...")
    vcs = HybridVCS()
    print(f"   Repository initialized at: {vcs.config['REPO_DIR']}")
    
    # Create main development branch
    print("\n2. Setting up main development branch...")
    try:
        vcs.create_branch("main_development")
        print("   Created 'main_development' branch")
    except Exception as e:
        print(f"   Branch may already exist: {e}")
    
    # Define multiple experiment configurations
    experiments = [
        {
            "id": "exp_001",
            "config": {
                "model_type": "cnn",
                "learning_rate": 0.001,
                "batch_size": 32,
                "optimizer": "adam"
            }
        },
        {
            "id": "exp_002", 
            "config": {
                "model_type": "rnn",
                "learning_rate": 0.0005,
                "batch_size": 64,
                "optimizer": "sgd"
            }
        },
        {
            "id": "exp_003",
            "config": {
                "model_type": "transformer",
                "learning_rate": 0.0001,
                "batch_size": 16,
                "optimizer": "adamw"
            }
        }
    ]
    
    # Run experiments in parallel
    print("\n3. Running parallel training experiments...")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for exp in experiments:
            future = executor.submit(simulate_training_experiment, vcs, exp["id"], exp["config"])
            futures.append(future)
        
        # Wait for all experiments to complete
        completed_experiments = []
        for future in futures:
            experiment_id = future.result()
            completed_experiments.append(experiment_id)
    
    elapsed_time = time.time() - start_time
    print(f"   All experiments completed in {elapsed_time:.2f} seconds")
    
    # Switch back to main branch
    print("\n4. Switching back to main development branch...")
    vcs.switch_branch("main_development")
    
    # Analyze experiment results
    print("\n5. Analyzing experiment results...")
    best_experiment = None
    best_accuracy = 0
    
    for exp in experiments:
        exp_id = exp["id"]
        final_state = vcs.load_state(f"{exp_id}_epoch_100")
        if final_state:
            accuracy = final_state["metrics"]["accuracy"]
            print(f"   {exp_id}: Final accuracy = {accuracy:.3f}")
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_experiment = exp_id
    
    print(f"   Best performing experiment: {best_experiment} (accuracy: {best_accuracy:.3f})")
    
    # Create a summary state
    print("\n6. Creating experiment summary...")
    summary_state = {
        "experiment_batch": "advanced_demo",
        "total_experiments": len(experiments),
        "best_experiment": best_experiment,
        "best_accuracy": best_accuracy,
        "completion_time": elapsed_time,
        "experiments": experiments
    }
    vcs.save_state("experiment_summary", summary_state)
    print("   Experiment summary saved")
    
    # Record overall feedback
    vcs.record_feedback(
        severity=9,
        category="experiment_batch_completion",
        params={
            "total_experiments": len(experiments),
            "best_accuracy": best_accuracy,
            "completion_time_seconds": elapsed_time,
            "parallel_execution": True
        }
    )
    
    # Show comprehensive status
    print("\n7. Repository status after experiments...")
    status = vcs.get_status()
    print(f"   Current branch: {status['current_branch']}")
    print(f"   Total branches: {len(status['branches'])}")
    print(f"   Available branches: {', '.join(status['branches'])}")
    print(f"   Recent commits: {len(status['recent_commits'])}")
    
    # Demonstrate state loading across experiments
    print("\n8. Cross-experiment state analysis...")
    all_final_states = []
    for exp in experiments:
        state = vcs.load_state(f"{exp['id']}_epoch_100")
        if state:
            all_final_states.append(state)
    
    if all_final_states:
        avg_accuracy = sum(s["metrics"]["accuracy"] for s in all_final_states) / len(all_final_states)
        avg_loss = sum(s["metrics"]["loss"] for s in all_final_states) / len(all_final_states)
        print(f"   Average final accuracy: {avg_accuracy:.3f}")
        print(f"   Average final loss: {avg_loss:.3f}")
    
    # Cleanup
    vcs.cleanup()
    print("\n=== Advanced example completed successfully! ===")


if __name__ == "__main__":
    main()
