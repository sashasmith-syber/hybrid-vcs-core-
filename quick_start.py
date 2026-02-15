"""
Quick Start Demo for Hybrid VCS
Demonstrates basic functionality with sample operations
"""

import json
import time
from colorama import init, Fore, Style
from hybrid_vcs_original import HybridVCS

# Initialize colorama
init()

def print_header(title):
    """Print a formatted header"""
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{title}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

def print_step(step_num, description):
    """Print a step description"""
    print(f"{Fore.YELLOW}Step {step_num}: {description}{Style.RESET_ALL}")

def print_result(result):
    """Print operation result"""
    if isinstance(result, dict):
        if 'error' in result:
            print(f"{Fore.RED}❌ Error: {result['error']}{Style.RESET_ALL}")
        elif 'success' in result:
            print(f"{Fore.GREEN}✅ Success!{Style.RESET_ALL}")
            for key, value in result.items():
                if key != 'success':
                    print(f"   {key}: {value}")
        else:
            print(json.dumps(result, indent=2))
    else:
        print(result)
    print()

def quick_start_demo():
    """Run a complete quick start demonstration"""
    print_header("🚀 Hybrid VCS Quick Start Demo")
    
    # Initialize VCS
    vcs = HybridVCS(repo_path="./demo_repos")
    
    # Step 1: Initialize a repository
    print_step(1, "Initialize a new repository")
    result = vcs.init_repository("demo-project")
    print_result(result)
    time.sleep(1)
    
    # Step 2: Add some files
    print_step(2, "Add files to the repository")
    
    # Add README
    readme_content = b"""# Demo Project
    
This is a demonstration project for Hybrid VCS.

## Features
- Version control
- Branching and merging
- Distributed architecture
"""
    result = vcs.add_file("demo-project", "README.md", readme_content)
    print_result(result)
    
    # Add a Python file
    python_content = b"""def hello_world():
    print("Hello from Hybrid VCS!")

if __name__ == "__main__":
    hello_world()
"""
    result = vcs.add_file("demo-project", "main.py", python_content)
    print_result(result)
    time.sleep(1)
    
    # Step 3: Commit changes
    print_step(3, "Commit the staged changes")
    result = vcs.commit(
        "demo-project",
        "Initial commit: Add README and main.py",
        "Demo User"
    )
    print_result(result)
    time.sleep(1)
    
    # Step 4: Create a new branch
    print_step(4, "Create a feature branch")
    result = vcs.create_branch("demo-project", "feature/new-feature")
    print_result(result)
    time.sleep(1)
    
    # Step 5: Switch to the new branch
    print_step(5, "Switch to the feature branch")
    result = vcs.checkout("demo-project", "feature/new-feature")
    print_result(result)
    time.sleep(1)
    
    # Step 6: Make more changes on the feature branch
    print_step(6, "Add more files on the feature branch")
    
    feature_content = b"""def new_feature():
    return "This is a new feature!"
"""
    result = vcs.add_file("demo-project", "feature.py", feature_content)
    print_result(result)
    
    result = vcs.commit(
        "demo-project",
        "Add new feature implementation",
        "Demo User"
    )
    print_result(result)
    time.sleep(1)
    
    # Step 7: View repository status
    print_step(7, "Check repository status")
    result = vcs.get_status("demo-project")
    print_result(result)
    time.sleep(1)
    
    # Step 8: View commit history
    print_step(8, "View commit history")
    result = vcs.get_history("demo-project")
    print(f"{Fore.CYAN}Commit History:{Style.RESET_ALL}")
    for i, commit in enumerate(result.get('commits', []), 1):
        print(f"\n{Fore.YELLOW}Commit #{i}:{Style.RESET_ALL}")
        print(f"  ID: {commit['id'][:12]}...")
        print(f"  Author: {commit['author']}")
        print(f"  Date: {commit['timestamp']}")
        print(f"  Message: {commit['message']}")
        print(f"  Branch: {commit['branch']}")
    print()
    time.sleep(1)
    
    # Step 9: List all repositories
    print_step(9, "List all repositories")
    repos = vcs.list_repositories()
    print(f"{Fore.CYAN}Repositories:{Style.RESET_ALL}")
    for repo in repos:
        print(f"\n{Fore.GREEN}📦 {repo['name']}{Style.RESET_ALL}")
        print(f"   Created: {repo['created']}")
        print(f"   Branches: {', '.join(repo['branches'])}")
        print(f"   Commits: {repo['commits']}")
    print()
    
    # Summary
    print_header("✨ Demo Complete!")
    print(f"{Fore.GREEN}Successfully demonstrated:{Style.RESET_ALL}")
    print(f"  ✓ Repository initialization")
    print(f"  ✓ File staging and commits")
    print(f"  ✓ Branch creation and switching")
    print(f"  ✓ Commit history tracking")
    print(f"  ✓ Repository management")
    print()
    print(f"{Fore.CYAN}Try the web interface:{Style.RESET_ALL}")
    print(f"  python app.py")
    print()
    print(f"{Fore.CYAN}Or run the development server:{Style.RESET_ALL}")
    print(f"  python run_local.py")
    print()

def interactive_mode():
    """Run interactive mode for user experimentation"""
    print_header("🎮 Hybrid VCS Interactive Mode")
    
    vcs = HybridVCS()
    
    while True:
        print(f"\n{Fore.CYAN}Available Commands:{Style.RESET_ALL}")
        print("  1. Initialize repository")
        print("  2. List repositories")
        print("  3. View repository status")
        print("  4. Run quick demo")
        print("  5. Exit")
        
        choice = input(f"\n{Fore.YELLOW}Enter your choice (1-5): {Style.RESET_ALL}")
        
        if choice == '1':
            repo_name = input(f"{Fore.YELLOW}Repository name: {Style.RESET_ALL}")
            result = vcs.init_repository(repo_name)
            print_result(result)
        
        elif choice == '2':
            repos = vcs.list_repositories()
            print_result(repos)
        
        elif choice == '3':
            repo_name = input(f"{Fore.YELLOW}Repository name: {Style.RESET_ALL}")
            result = vcs.get_status(repo_name)
            print_result(result)
        
        elif choice == '4':
            quick_start_demo()
        
        elif choice == '5':
            print(f"\n{Fore.GREEN}Goodbye!{Style.RESET_ALL}\n")
            break
        
        else:
            print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hybrid VCS Quick Start')
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    else:
        quick_start_demo()

if __name__ == '__main__':
    main()
