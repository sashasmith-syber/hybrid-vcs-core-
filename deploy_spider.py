"""
Spider Deployment Orchestrator
Manages deployment and scheduling of spider crawls
"""

import json
import sys
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from colorama import init, Fore, Style

# Initialize colorama
init()


class SpiderDeployer:
    """
    Orchestrates spider deployments and scheduling
    
    Features:
    - Deploy spider configurations
    - Schedule periodic crawls
    - Monitor spider health
    - Manage multiple spider instances
    """
    
    def __init__(self, config_dir: str = "./spider_configs"):
        """Initialize the deployer"""
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.deployments_file = self.config_dir / "deployments.json"
        self.deployments = self._load_deployments()
    
    def _load_deployments(self) -> Dict[str, Any]:
        """Load deployment configurations"""
        if self.deployments_file.exists():
            with open(self.deployments_file, 'r') as f:
                return json.load(f)
        return {"spiders": {}, "version": "1.0.0"}
    
    def _save_deployments(self):
        """Save deployment configurations"""
        with open(self.deployments_file, 'w') as f:
            json.dump(self.deployments, f, indent=2)
    
    def create_deployment(
        self,
        name: str,
        start_url: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new spider deployment
        
        Args:
            name: Deployment name
            start_url: Starting URL for the spider
            config: Optional spider configuration
            
        Returns:
            Deployment information
        """
        if name in self.deployments['spiders']:
            return {"error": f"Deployment '{name}' already exists"}
        
        # Create deployment configuration
        deployment = {
            "name": name,
            "start_url": start_url,
            "config": config or {},
            "created": datetime.now().isoformat(),
            "last_run": None,
            "status": "created",
            "runs": []
        }
        
        # Save spider-specific config
        config_file = self.config_dir / f"{name}_config.json"
        with open(config_file, 'w') as f:
            json.dump(config or {}, f, indent=2)
        
        self.deployments['spiders'][name] = deployment
        self._save_deployments()
        
        return {
            "success": True,
            "deployment": name,
            "config_file": str(config_file)
        }
    
    def run_deployment(self, name: str, async_mode: bool = False) -> Dict[str, Any]:
        """
        Run a spider deployment
        
        Args:
            name: Deployment name
            async_mode: Run in background if True
            
        Returns:
            Run result
        """
        if name not in self.deployments['spiders']:
            return {"error": f"Deployment '{name}' not found"}
        
        deployment = self.deployments['spiders'][name]
        config_file = self.config_dir / f"{name}_config.json"
        
        print(f"{Fore.CYAN}Starting spider: {name}{Style.RESET_ALL}")
        print(f"URL: {deployment['start_url']}")
        print(f"Config: {config_file}")
        
        # Prepare command
        cmd = [
            sys.executable,
            "spider_entity.py",
            deployment['start_url'],
            "--config", str(config_file),
            "--repo", f"spider-{name}"
        ]
        
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            if async_mode:
                # Run in background
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                result = {
                    "success": True,
                    "run_id": run_id,
                    "pid": process.pid,
                    "status": "running",
                    "async": True
                }
            else:
                # Run synchronously
                result_proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                result = {
                    "success": result_proc.returncode == 0,
                    "run_id": run_id,
                    "status": "completed" if result_proc.returncode == 0 else "failed",
                    "output": result_proc.stdout,
                    "error": result_proc.stderr if result_proc.returncode != 0 else None
                }
            
            # Update deployment
            deployment['last_run'] = datetime.now().isoformat()
            deployment['status'] = result['status']
            deployment['runs'].append({
                "run_id": run_id,
                "timestamp": datetime.now().isoformat(),
                "status": result['status']
            })
            self._save_deployments()
            
            return result
        
        except subprocess.TimeoutExpired:
            return {
                "error": "Spider execution timed out",
                "run_id": run_id
            }
        except Exception as e:
            return {
                "error": str(e),
                "run_id": run_id
            }
    
    def list_deployments(self) -> List[Dict[str, Any]]:
        """List all deployments"""
        deployments = []
        for name, deployment in self.deployments['spiders'].items():
            deployments.append({
                "name": name,
                "start_url": deployment['start_url'],
                "status": deployment['status'],
                "created": deployment['created'],
                "last_run": deployment['last_run'],
                "total_runs": len(deployment['runs'])
            })
        return deployments
    
    def get_deployment_status(self, name: str) -> Dict[str, Any]:
        """Get detailed status of a deployment"""
        if name not in self.deployments['spiders']:
            return {"error": f"Deployment '{name}' not found"}
        
        deployment = self.deployments['spiders'][name]
        return {
            "deployment": name,
            "status": deployment['status'],
            "last_run": deployment['last_run'],
            "runs": deployment['runs'][-10:],  # Last 10 runs
            "config": deployment['config']
        }
    
    def delete_deployment(self, name: str) -> Dict[str, Any]:
        """Delete a deployment"""
        if name not in self.deployments['spiders']:
            return {"error": f"Deployment '{name}' not found"}
        
        # Remove config file
        config_file = self.config_dir / f"{name}_config.json"
        if config_file.exists():
            config_file.unlink()
        
        # Remove from deployments
        del self.deployments['spiders'][name]
        self._save_deployments()
        
        return {
            "success": True,
            "message": f"Deployment '{name}' deleted"
        }
    
    def schedule_deployment(
        self,
        name: str,
        cron_expression: str
    ) -> Dict[str, Any]:
        """
        Schedule a deployment (placeholder for future implementation)
        
        Args:
            name: Deployment name
            cron_expression: Cron expression for scheduling
            
        Returns:
            Schedule result
        """
        if name not in self.deployments['spiders']:
            return {"error": f"Deployment '{name}' not found"}
        
        deployment = self.deployments['spiders'][name]
        deployment['schedule'] = {
            "enabled": True,
            "cron": cron_expression,
            "next_run": None  # Would be calculated from cron
        }
        self._save_deployments()
        
        return {
            "success": True,
            "message": f"Scheduled '{name}' with cron: {cron_expression}",
            "note": "Actual scheduling requires a cron daemon or task scheduler"
        }


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Spider Deployment Orchestrator')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create deployment
    create_parser = subparsers.add_parser('create', help='Create a new deployment')
    create_parser.add_argument('name', help='Deployment name')
    create_parser.add_argument('url', help='Start URL')
    create_parser.add_argument('--config', help='Config file to copy')
    
    # Run deployment
    run_parser = subparsers.add_parser('run', help='Run a deployment')
    run_parser.add_argument('name', help='Deployment name')
    run_parser.add_argument('--async', action='store_true', help='Run in background')
    
    # List deployments
    subparsers.add_parser('list', help='List all deployments')
    
    # Status
    status_parser = subparsers.add_parser('status', help='Get deployment status')
    status_parser.add_argument('name', help='Deployment name')
    
    # Delete
    delete_parser = subparsers.add_parser('delete', help='Delete a deployment')
    delete_parser.add_argument('name', help='Deployment name')
    
    args = parser.parse_args()
    
    deployer = SpiderDeployer()
    
    if args.command == 'create':
        config = None
        if args.config:
            with open(args.config, 'r') as f:
                config = json.load(f)
        result = deployer.create_deployment(args.name, args.url, config)
        print(json.dumps(result, indent=2))
    
    elif args.command == 'run':
        result = deployer.run_deployment(args.name, getattr(args, 'async', False))
        print(json.dumps(result, indent=2))
    
    elif args.command == 'list':
        deployments = deployer.list_deployments()
        print(json.dumps(deployments, indent=2))
    
    elif args.command == 'status':
        result = deployer.get_deployment_status(args.name)
        print(json.dumps(result, indent=2))
    
    elif args.command == 'delete':
        result = deployer.delete_deployment(args.name)
        print(json.dumps(result, indent=2))
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
