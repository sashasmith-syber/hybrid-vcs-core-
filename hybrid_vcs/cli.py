"""
Command Line Interface for Hybrid VCS.
"""

import argparse
import json
import logging
import os
import sys
from typing import List

from .core import HybridVCS
from .web_server import create_server
from .config import CONFIG, update_config


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
    )


def cmd_init(args):
    """Initialize a new Hybrid VCS repository."""
    if args.repo_dir:
        update_config({"REPO_DIR": os.path.abspath(args.repo_dir)})
    
    vcs = HybridVCS()
    print(f"Initialized Hybrid VCS repository at: {vcs.config['REPO_DIR']}")


def cmd_save(args):
    """Save files to version control."""
    vcs = HybridVCS()
    
    # Validate files exist
    for file_path in args.files:
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            sys.exit(1)
    
    try:
        commit_hash = vcs.save_version(args.files, args.message)
        print(f"Files saved with commit: {commit_hash}")
    except Exception as e:
        print(f"Error saving files: {e}")
        sys.exit(1)


def cmd_load(args):
    """Load files from a specific commit."""
    vcs = HybridVCS()
    
    try:
        files_data = vcs.get_version(args.commit)
        print(f"Retrieved {len(files_data)} files from commit {args.commit}")
        
        if args.output_dir:
            os.makedirs(args.output_dir, exist_ok=True)
            for i, data in enumerate(files_data):
                output_path = os.path.join(args.output_dir, f"file_{i}.bin")
                with open(output_path, "wb") as f:
                    f.write(data)
                print(f"Saved file to: {output_path}")
        else:
            print(f"File sizes: {[len(data) for data in files_data]} bytes")
            
    except Exception as e:
        print(f"Error loading files: {e}")
        sys.exit(1)


def cmd_state_save(args):
    """Save state configuration."""
    vcs = HybridVCS()
    
    try:
        # Parse JSON from file or command line
        if args.file:
            with open(args.file, 'r') as f:
                state_data = json.load(f)
        else:
            state_data = json.loads(args.data)
        
        vcs.save_state(args.key, state_data)
        print(f"State saved: {args.key}")
        
    except Exception as e:
        print(f"Error saving state: {e}")
        sys.exit(1)


def cmd_state_load(args):
    """Load state configuration."""
    vcs = HybridVCS()
    
    try:
        state_data = vcs.load_state(args.key)
        if state_data is None:
            print(f"State not found: {args.key}")
            sys.exit(1)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(state_data, f, indent=2)
            print(f"State saved to: {args.output}")
        else:
            print(json.dumps(state_data, indent=2))
            
    except Exception as e:
        print(f"Error loading state: {e}")
        sys.exit(1)


def cmd_feedback(args):
    """Record feedback/telemetry."""
    vcs = HybridVCS()
    
    try:
        params = json.loads(args.params) if args.params else {}
        vcs.record_feedback(args.severity, args.category, params, args.commit)
        print(f"Feedback recorded: {args.category}")
        
    except Exception as e:
        print(f"Error recording feedback: {e}")
        sys.exit(1)


def cmd_branch(args):
    """Branch operations."""
    vcs = HybridVCS()
    
    try:
        if args.action == 'create':
            vcs.create_branch(args.name)
            print(f"Created branch: {args.name}")
        elif args.action == 'switch':
            vcs.switch_branch(args.name)
            print(f"Switched to branch: {args.name}")
        elif args.action == 'list':
            status = vcs.get_status()
            print(f"Current branch: {status['current_branch']}")
            print("All branches:")
            for branch in status['branches']:
                marker = "* " if branch == status['current_branch'] else "  "
                print(f"{marker}{branch}")
                
    except Exception as e:
        print(f"Error with branch operation: {e}")
        sys.exit(1)


def cmd_status(args):
    """Show repository status."""
    vcs = HybridVCS()

    try:
        status = vcs.get_status()
        print(json.dumps(status, indent=2, default=str))

    except Exception as e:
        print(f"Error getting status: {e}")
        sys.exit(1)


def cmd_server(args):
    """Start the web server for browser extension API."""
    import time

    try:
        print("Starting Hybrid VCS Web Server...")
        print(f"Host: {args.host}")
        print(f"Port: {args.port}")
        print("Press Ctrl+C to stop")

        server = create_server(host=args.host, port=args.port)
        server.start()

        # Keep running until interrupted
        try:
            while server.is_running():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping server...")
        finally:
            server.stop()
            print("Server stopped.")

    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Hybrid VCS - Git + SQLite Version Control")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize repository")
    init_parser.add_argument("--repo-dir", help="Repository directory")
    init_parser.set_defaults(func=cmd_init)
    
    # Save command
    save_parser = subparsers.add_parser("save", help="Save files")
    save_parser.add_argument("files", nargs="+", help="Files to save")
    save_parser.add_argument("-m", "--message", required=True, help="Commit message")
    save_parser.set_defaults(func=cmd_save)
    
    # Load command
    load_parser = subparsers.add_parser("load", help="Load files from commit")
    load_parser.add_argument("commit", help="Commit hash")
    load_parser.add_argument("-o", "--output-dir", help="Output directory for files")
    load_parser.set_defaults(func=cmd_load)
    
    # State save command
    state_save_parser = subparsers.add_parser("state-save", help="Save state")
    state_save_parser.add_argument("key", help="State key")
    state_save_group = state_save_parser.add_mutually_exclusive_group(required=True)
    state_save_group.add_argument("-d", "--data", help="JSON data string")
    state_save_group.add_argument("-f", "--file", help="JSON file path")
    state_save_parser.set_defaults(func=cmd_state_save)
    
    # State load command
    state_load_parser = subparsers.add_parser("state-load", help="Load state")
    state_load_parser.add_argument("key", help="State key")
    state_load_parser.add_argument("-o", "--output", help="Output file path")
    state_load_parser.set_defaults(func=cmd_state_load)
    
    # Feedback command
    feedback_parser = subparsers.add_parser("feedback", help="Record feedback")
    feedback_parser.add_argument("severity", type=int, help="Severity (0-10)")
    feedback_parser.add_argument("category", help="Feedback category")
    feedback_parser.add_argument("-p", "--params", help="JSON parameters")
    feedback_parser.add_argument("-c", "--commit", help="Commit hash")
    feedback_parser.set_defaults(func=cmd_feedback)
    
    # Branch command
    branch_parser = subparsers.add_parser("branch", help="Branch operations")
    branch_parser.add_argument("action", choices=["create", "switch", "list"], help="Branch action")
    branch_parser.add_argument("name", nargs="?", help="Branch name")
    branch_parser.set_defaults(func=cmd_branch)
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show status")
    status_parser.set_defaults(func=cmd_status)

    # Server command
    server_parser = subparsers.add_parser("server", help="Start web server for browser extension")
    server_parser.add_argument("--host", default="localhost", help="Server host (default: localhost)")
    server_parser.add_argument("--port", type=int, default=8080, help="Server port (default: 8080)")
    server_parser.set_defaults(func=cmd_server)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    setup_logging(args.verbose)
    args.func(args)


if __name__ == "__main__":
    main()
