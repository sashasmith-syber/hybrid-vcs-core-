"""
Production Status Dashboard
Displays system status and health metrics
"""

import os
import sys
import json
import psutil
from datetime import datetime
from pathlib import Path
from colorama import init, Fore, Style
from hybrid_vcs_original import HybridVCS

# Initialize colorama
init()


class StatusDashboard:
    """Display production status and health metrics"""
    
    def __init__(self):
        self.vcs = HybridVCS()
    
    def get_system_info(self):
        """Get system information"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_usage": f"{cpu_percent}%",
            "memory_total": f"{memory.total / (1024**3):.2f} GB",
            "memory_used": f"{memory.used / (1024**3):.2f} GB",
            "memory_percent": f"{memory.percent}%",
            "disk_total": f"{disk.total / (1024**3):.2f} GB",
            "disk_used": f"{disk.used / (1024**3):.2f} GB",
            "disk_percent": f"{disk.percent}%"
        }
    
    def get_vcs_stats(self):
        """Get VCS statistics"""
        repos = self.vcs.list_repositories()
        
        total_commits = sum(repo['commits'] for repo in repos)
        total_branches = sum(len(repo['branches']) for repo in repos)
        
        return {
            "total_repositories": len(repos),
            "total_commits": total_commits,
            "total_branches": total_branches,
            "repositories": repos
        }
    
    def check_services(self):
        """Check if services are running"""
        services = {}
        
        # Check if app.py is running
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and 'app.py' in ' '.join(cmdline):
                    services['web_server'] = {
                        "status": "running",
                        "pid": proc.info['pid']
                    }
                elif cmdline and 'spider_entity.py' in ' '.join(cmdline):
                    services['spider'] = {
                        "status": "running",
                        "pid": proc.info['pid']
                    }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if 'web_server' not in services:
            services['web_server'] = {"status": "stopped"}
        if 'spider' not in services:
            services['spider'] = {"status": "stopped"}
        
        return services
    
    def print_header(self, title):
        """Print section header"""
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{title:^70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    def print_status_line(self, label, value, status="info"):
        """Print a status line"""
        colors = {
            "info": Fore.CYAN,
            "success": Fore.GREEN,
            "warning": Fore.YELLOW,
            "error": Fore.RED
        }
        color = colors.get(status, Fore.WHITE)
        print(f"  {label:.<40} {color}{value}{Style.RESET_ALL}")
    
    def display_dashboard(self):
        """Display the complete status dashboard"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Header
        print(f"\n{Fore.YELLOW}{'*'*70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'HYBRID VCS - PRODUCTION STATUS DASHBOARD':^70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{timestamp:^70}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'*'*70}{Style.RESET_ALL}")
        
        # System Information
        self.print_header("SYSTEM INFORMATION")
        sys_info = self.get_system_info()
        
        cpu_status = "success" if float(sys_info["cpu_usage"].rstrip('%')) < 80 else "warning"
        self.print_status_line("CPU Usage", sys_info["cpu_usage"], cpu_status)
        
        mem_status = "success" if float(sys_info["memory_percent"].rstrip('%')) < 80 else "warning"
        self.print_status_line("Memory Usage", f"{sys_info['memory_used']} / {sys_info['memory_total']} ({sys_info['memory_percent']})", mem_status)
        
        disk_status = "success" if float(sys_info["disk_percent"].rstrip('%')) < 80 else "warning"
        self.print_status_line("Disk Usage", f"{sys_info['disk_used']} / {sys_info['disk_total']} ({sys_info['disk_percent']})", disk_status)
        
        # Service Status
        self.print_header("SERVICE STATUS")
        services = self.check_services()
        
        for service_name, service_info in services.items():
            status = service_info['status']
            status_type = "success" if status == "running" else "warning"
            
            if status == "running":
                value = f"{status.upper()} (PID: {service_info['pid']})"
            else:
                value = status.upper()
            
            label = service_name.replace('_', ' ').title()
            self.print_status_line(label, value, status_type)
        
        # VCS Statistics
        self.print_header("VERSION CONTROL STATISTICS")
        vcs_stats = self.get_vcs_stats()
        
        self.print_status_line("Total Repositories", str(vcs_stats['total_repositories']), "info")
        self.print_status_line("Total Commits", str(vcs_stats['total_commits']), "info")
        self.print_status_line("Total Branches", str(vcs_stats['total_branches']), "info")
        
        # Repository Details
        if vcs_stats['repositories']:
            self.print_header("REPOSITORY DETAILS")
            for repo in vcs_stats['repositories']:
                print(f"\n  {Fore.YELLOW}📦 {repo['name']}{Style.RESET_ALL}")
                print(f"     Created: {repo['created']}")
                print(f"     Branches: {', '.join(repo['branches'])}")
                print(f"     Commits: {repo['commits']}")
        
        # Health Check Summary
        self.print_header("HEALTH CHECK SUMMARY")
        
        # Overall health
        warnings = 0
        if float(sys_info["cpu_usage"].rstrip('%')) >= 80:
            warnings += 1
        if float(sys_info["memory_percent"].rstrip('%')) >= 80:
            warnings += 1
        if float(sys_info["disk_percent"].rstrip('%')) >= 80:
            warnings += 1
        if services['web_server']['status'] != 'running':
            warnings += 1
        
        if warnings == 0:
            health = "HEALTHY"
            health_status = "success"
        elif warnings <= 2:
            health = "WARNING"
            health_status = "warning"
        else:
            health = "CRITICAL"
            health_status = "error"
        
        self.print_status_line("Overall Status", health, health_status)
        self.print_status_line("Active Warnings", str(warnings), "info" if warnings == 0 else "warning")
        
        # Footer
        print(f"\n{Fore.YELLOW}{'*'*70}{Style.RESET_ALL}\n")
        
        return {
            "status": health,
            "warnings": warnings,
            "system": sys_info,
            "services": services,
            "vcs": vcs_stats,
            "timestamp": timestamp
        }
    
    def export_json(self, output_file: str):
        """Export status as JSON"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "system": self.get_system_info(),
            "services": self.check_services(),
            "vcs": self.get_vcs_stats()
        }
        
        with open(output_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        print(f"{Fore.GREEN}✓ Status exported to {output_file}{Style.RESET_ALL}")
        return status


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hybrid VCS Status Dashboard')
    parser.add_argument(
        '--export',
        metavar='FILE',
        help='Export status as JSON to file'
    )
    parser.add_argument(
        '--watch',
        action='store_true',
        help='Watch mode - refresh every 5 seconds'
    )
    
    args = parser.parse_args()
    
    dashboard = StatusDashboard()
    
    if args.export:
        dashboard.export_json(args.export)
    elif args.watch:
        import time
        try:
            while True:
                os.system('clear' if os.name == 'posix' else 'cls')
                dashboard.display_dashboard()
                print(f"{Fore.CYAN}Refreshing in 5 seconds... (Press Ctrl+C to stop){Style.RESET_ALL}")
                time.sleep(5)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Stopped watching{Style.RESET_ALL}\n")
    else:
        dashboard.display_dashboard()


if __name__ == '__main__':
    main()
