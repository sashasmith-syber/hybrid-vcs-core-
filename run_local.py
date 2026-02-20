"""
Development Server with Hot Reload
Watches for file changes and automatically restarts the server
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from colorama import init, Fore, Style

# Initialize colorama
init()

class ServerReloadHandler(FileSystemEventHandler):
    """Handle file system events and trigger server reload"""
    
    def __init__(self, restart_callback):
        self.restart_callback = restart_callback
        self.last_reload = 0
        self.debounce_seconds = 1  # Prevent multiple rapid reloads
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Only reload for Python files
        if not event.src_path.endswith('.py'):
            return
        
        # Debounce rapid changes
        current_time = time.time()
        if current_time - self.last_reload < self.debounce_seconds:
            return
        
        self.last_reload = current_time
        
        print(f"\n{Fore.YELLOW}📝 File changed: {event.src_path}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🔄 Reloading server...{Style.RESET_ALL}\n")
        self.restart_callback()

class DevelopmentServer:
    """Development server with hot reload capability"""
    
    def __init__(self, app_module='app', port=5000, watch_dirs=None):
        self.app_module = app_module
        self.port = port
        self.watch_dirs = watch_dirs or ['.']
        self.process = None
        self.observer = None
    
    def start_server(self):
        """Start the Flask server process"""
        if self.process:
            self.stop_server()
        
        env = os.environ.copy()
        env['FLASK_APP'] = self.app_module
        env['FLASK_ENV'] = 'development'
        env['PORT'] = str(self.port)
        env['DEBUG'] = 'True'
        
        self.process = subprocess.Popen(
            [sys.executable, f'{self.app_module}.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Print server output
        if self.process.stdout:
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    print(line, end='')
                if "Starting Hybrid VCS Server" in line or "Running on" in line:
                    break
    
    def stop_server(self):
        """Stop the Flask server process"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
    
    def watch_files(self):
        """Start watching files for changes"""
        self.observer = Observer()
        handler = ServerReloadHandler(self.start_server)
        
        for watch_dir in self.watch_dirs:
            path = Path(watch_dir).resolve()
            if path.exists():
                self.observer.schedule(handler, str(path), recursive=True)
                print(f"{Fore.GREEN}👁️  Watching: {path}{Style.RESET_ALL}")
        
        self.observer.start()
    
    def run(self):
        """Run the development server with hot reload"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🚀 Hybrid VCS Development Server{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}⚙️  Configuration:{Style.RESET_ALL}")
        print(f"   Port: {self.port}")
        print(f"   App Module: {self.app_module}")
        print(f"   Hot Reload: Enabled")
        print(f"\n{Fore.GREEN}🌐 Server URL: http://localhost:{self.port}/{Style.RESET_ALL}\n")
        
        try:
            # Start initial server
            self.start_server()
            
            # Start file watcher
            self.watch_files()
            
            print(f"{Fore.YELLOW}⚡ Hot reload is active. Watching for file changes...{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Press Ctrl+C to stop the server{Style.RESET_ALL}\n")
            
            # Keep the main thread alive
            while True:
                time.sleep(1)
                
                # Check if process is still running
                if self.process and self.process.poll() is not None:
                    print(f"\n{Fore.RED}❌ Server process died unexpectedly{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}🔄 Restarting...{Style.RESET_ALL}\n")
                    self.start_server()
        
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}⏹️  Shutting down development server...{Style.RESET_ALL}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        self.stop_server()
        print(f"{Fore.GREEN}✅ Server stopped successfully{Style.RESET_ALL}\n")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hybrid VCS Development Server')
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to run the server on (default: 5000)'
    )
    parser.add_argument(
        '--app',
        default='app',
        help='App module to run (default: app)'
    )
    parser.add_argument(
        '--watch',
        nargs='+',
        default=['.'],
        help='Directories to watch for changes (default: current directory)'
    )
    
    args = parser.parse_args()
    
    server = DevelopmentServer(
        app_module=args.app,
        port=args.port,
        watch_dirs=args.watch
    )
    
    server.run()

if __name__ == '__main__':
    main()
