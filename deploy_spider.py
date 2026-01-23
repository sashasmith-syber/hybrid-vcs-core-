#!/usr/bin/env python3
"""
Spider Entity Deployment Script
Automated deployment system for the Spider Entity web crawler
"""

import os
import sys
import subprocess
import json
import argparse
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('spider_deployer')

class SpiderDeployer:
    """Deployment system for Spider Entity"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent
        self.config_file = self.project_root / "spider_config.json"
        self.deployment_dir = self.project_root / "spider_deployment"
        
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed"""
        required_packages = [
            'aiohttp',
            'asyncio',
            'sqlite3',
            'logging',
            'pathlib',
            'argparse'
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)
                
        if missing:
            logger.error(f"Missing dependencies: {missing}")
            return False
            
        return True
        
    def create_deployment_structure(self):
        """Create deployment directory structure"""
        self.deployment_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.deployment_dir / "logs").mkdir(exist_ok=True)
        (self.deployment_dir / "data").mkdir(exist_ok=True)
        (self.deployment_dir / "config").mkdir(exist_ok=True)
        
        logger.info("Deployment structure created")
        
    def create_config_template(self):
        """Create configuration template"""
        config = {
            "spider": {
                "max_depth": 3,
                "max_pages": 1000,
                "delay": 1.0,
                "user_agent": "SpiderEntity/1.0 (Hybrid VCS)",
                "respect_robots": True
            },
            "deployment": {
                "port": 8080,
                "host": "localhost",
                "log_level": "INFO",
                "database_path": "spider_deployment/data/spider.db"
            },
            "monitoring": {
                "enable_metrics": True,
                "metrics_port": 9090,
                "health_check_interval": 30
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        logger.info("Configuration template created")
        
    def create_systemd_service(self):
        """Create systemd service file for Linux deployment"""
        service_content = """[Unit]
Description=Spider Entity Web Crawler
After=network.target

[Service]
Type=simple
User=spider
WorkingDirectory={project_root}
ExecStart={python_path} {spider_path} --config {config_path}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
""".format(
            project_root=self.project_root,
            python_path=sys.executable,
            spider_path=self.project_root / "spider_entity.py",
            config_path=self.deployment_dir / "config" / "spider.json"
        )
        
        service_file = self.deployment_dir / "spider-entity.service"
        with open(service_file, 'w') as f:
            f.write(service_content)
            
        logger.info("Systemd service file created")
        
    def create_docker_compose(self):
        """Create Docker Compose configuration"""
        compose_content = """version: '3.8'

services:
  spider-entity:
    build: .
    container_name: spider-entity
    volumes:
      - ./spider_deployment/data:/app/data
      - ./spider_deployment/logs:/app/logs
      - ./spider_deployment/config:/app/config
    ports:
      - "8080:8080"
      - "9090:9090"
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    container_name: spider-prometheus
    ports:
      - "9091:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    depends_on:
      - spider-entity

  grafana:
    image: grafana/grafana:latest
    container_name: spider-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana

volumes:
  grafana-storage:
"""
        
        compose_file = self.deployment_dir / "docker-compose.yml"
        with open(compose_file, 'w') as f:
            f.write(compose_content)
            
        logger.info("Docker Compose configuration created")
        
    def create_dockerfile(self):
        """Create Dockerfile for containerized deployment"""
        dockerfile_content = """FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY spider_entity.py .
COPY hybrid-vcs-project/ ./hybrid-vcs-project/

# Create non-root user
RUN useradd -m -u 1000 spider

# Create directories
RUN mkdir -p /app/data /app/logs /app/config && \
    chown -R spider:spider /app

USER spider

EXPOSE 8080 9090

CMD ["python", "spider_entity.py", "--config", "/app/config/spider.json"]
"""
        
        dockerfile = self.deployment_dir / "Dockerfile"
        with open(dockerfile, 'w') as f:
            f.write(dockerfile_content)
            
        logger.info("Dockerfile created")
        
    def create_startup_script(self):
        """Create startup script for easy deployment"""
        startup_script = """#!/bin/bash
# Spider Entity Startup Script

set -e

echo "Starting Spider Entity deployment..."

# Check if config exists
if [ ! -f "spider_deployment/config/spider.json" ]; then
    echo "Creating default configuration..."
    cp spider_config.json spider_deployment/config/spider.json
fi

# Start with Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "Starting with Docker Compose..."
    docker-compose -f spider_deployment/docker-compose.yml up -d
elif command -v docker &> /dev/null; then
    echo "Starting with Docker..."
    docker build -t spider-entity .
    docker run -d \
        --name spider-entity \
        -p 8080:8080 \
        -p 9090:9090 \
        -v $(pwd)/spider_deployment/data:/app/data \
        -v $(pwd)/spider_deployment/logs:/app/logs \
        -v $(pwd)/spider_deployment/config:/app/config \
        spider-entity
else
    echo "Starting locally..."
    python spider_entity.py --config spider_deployment/config/spider.json
fi

echo "Spider Entity started successfully!"
echo "Check logs: tail -f spider_deployment/logs/spider.log"
"""
        
        startup_file = self.deployment_dir / "start_spider.sh"
        with open(startup_file, 'w') as f:
            f.write(startup_script)
            
        os.chmod(startup_file, 0o755)
        logger.info("Startup script created")
        
    def create_monitoring_config(self):
        """Create monitoring and alerting configuration"""
        prometheus_config = """global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'spider-entity'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: /metrics
    scrape_interval: 5s
"""
        
        prometheus_file = self.deployment_dir / "prometheus.yml"
        with open(prometheus_file, 'w') as f:
            f.write(prometheus_config)
            
        logger.info("Monitoring configuration created")
        
    def deploy(self, method: str = "local"):
        """Deploy Spider Entity using specified method"""
        logger.info(f"Starting deployment with method: {method}")
        
        if not self.check_dependencies():
            sys.exit(1)
            
        self.create_deployment_structure()
        self.create_config_template()
        self.create_dockerfile()
        self.create_docker_compose()
        self.create_systemd_service()
        self.create_startup_script()
        self.create_monitoring_config()
        
        if method == "docker":
            subprocess.run(["docker-compose", "-f", 
                          str(self.deployment_dir / "docker-compose.yml"), "up", "-d"])
        elif method == "local":
            subprocess.run([sys.executable, "spider_entity.py", 
                          "--config", str(self.deployment_dir / "config" / "spider.json")])
        elif method == "systemd":
            service_file = self.deployment_dir / "spider-entity.service"
            print(f"To install systemd service, run:")
            print(f"sudo cp {service_file} /etc/systemd/system/")
            print("sudo systemctl daemon-reload")
            print("sudo systemctl enable spider-entity")
            print("sudo systemctl start spider-entity")
            
        logger.info("Deployment complete!")

def main():
    parser = argparse.ArgumentParser(description='Deploy Spider Entity')
    parser.add_argument('--method', choices=['local', 'docker', 'systemd'], 
                       default='local', help='Deployment method')
    parser.add_argument('--project-root', default='.', 
                       help='Project root directory')
    
    args = parser.parse_args()
    
    deployer = SpiderDeployer(args.project_root)
    deployer.deploy(args.method)

if __name__ == "__main__":
    main()
