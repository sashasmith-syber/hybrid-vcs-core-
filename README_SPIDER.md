# Spider Entity - Hybrid VCS Web Crawler

## Overview

Spider Entity is a sophisticated web crawler integrated with the Hybrid VCS system, designed to automatically discover, crawl, and version web content while maintaining full Git history and compression capabilities.

## Features

- **Advanced Crawling**: Asynchronous web crawling with configurable depth and rate limiting
- **VCS Integration**: Automatic Git versioning of crawled content
- **Compression**: Built-in compression for efficient storage
- **Monitoring**: Real-time metrics and health checks
- **Flexible Deployment**: Multiple deployment options (local, Docker, systemd)
- **Database Storage**: SQLite database for crawl data and metadata
- **Robots.txt Compliance**: Respects robots.txt and crawl delays

## Quick Start

### 1. Deploy Spider Entity

```bash
# Local deployment
python deploy_spider.py --method local

# Docker deployment
python deploy_spider.py --method docker

# Systemd service
python deploy_spider.py --method systemd
```

### 2. Configure Spider

Edit `spider_config.json` to customize:
- Crawling parameters (depth, pages, delay)
- Target URLs
- Database settings
- Monitoring configuration

### 3. Start Crawling

```bash
# Direct execution
python spider_entity.py --config spider_config.json

# Using deployment script
./spider_deployment/start_spider.sh
```

## Configuration

### Spider Settings
```json
{
  "spider": {
    "max_depth": 3,
    "max_pages": 1000,
    "delay": 1.0,
    "user_agent": "SpiderEntity/1.0",
    "respect_robots": true,
    "start_urls": ["https://example.com"]
  }
}
```

### Deployment Options

#### Local Deployment
- Runs directly on host system
- Uses local Python environment
- SQLite database in project directory

#### Docker Deployment
- Containerized environment
- Isolated dependencies
- Volume mounts for persistent data

#### Systemd Service
- Background service
- Auto-start on boot
- System-level logging

## Architecture

```
spider_entity.py
├── SpiderEntity (Main crawler class)
├── Crawler (Async crawling engine)
├── DatabaseManager (SQLite storage)
├── GitIntegration (VCS operations)
├── CompressionEngine (Data compression)
└── Monitoring (Metrics & health checks)

deploy_spider.py
├── SpiderDeployer (Deployment orchestrator)
├── Docker support
├── Systemd integration
└── Monitoring setup
```

## Monitoring

### Metrics Endpoints
- **Health Check**: `http://localhost:8080/health`
- **Metrics**: `http://localhost:9090/metrics`
- **Status**: `http://localhost:8080/status`

### Grafana Dashboard
Access at `http://localhost:3000` (admin/admin)

## Storage Structure

```
spider_deployment/
├── data/
│   ├── spider.db          # SQLite database
│   └── crawled_content/   # Versioned content
├── logs/
│   ├── spider.log         # Application logs
│   └── metrics.log        # Performance metrics
├── config/
│   └── spider.json        # Configuration
└── git/
    └── .git/             # VCS repository
```

## API Endpoints

### REST API
- `GET /api/crawl/start` - Start crawling
- `GET /api/crawl/stop` - Stop crawling
- `GET /api/status` - Get crawler status
- `GET /api/metrics` - Get performance metrics
- `POST /api/config` - Update configuration

### WebSocket
- `ws://localhost:8080/ws` - Real-time updates

## Advanced Usage

### Custom Crawlers
```python
from spider_entity import SpiderEntity

spider = SpiderEntity(
    max_depth=5,
    max_pages=5000,
    custom_headers={'Authorization': 'Bearer token'}
)
spider.start_crawling(['https://target.com'])
```

### VCS Integration
```python
# Automatic commits every 100 pages
spider.enable_git_integration(
    repo_path='./crawl-repo',
    commit_frequency=100,
    commit_message_template='Crawl batch {batch_id}: {pages} pages'
)
```

### Compression Settings
```python
# Configure compression
spider.set_compression(
    algorithm='gzip',
    level=6,
    chunk_size=1024*1024  # 1MB chunks
)
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   chmod +x deploy_spider.py
   chmod +x spider_deployment/start_spider.sh
   ```

2. **Port Already in Use**
   - Change port in `spider_config.json`
   - Or kill existing process: `lsof -ti:8080 | xargs kill -9`

3. **Database Locked**
   - Stop spider: `pkill -f spider_entity`
   - Remove lock: `rm spider_deployment/data/spider.db-journal`

### Logs Location
- Application logs: `spider_deployment/logs/spider.log`
- System logs: `journalctl -u spider-entity` (systemd)
- Docker logs: `docker logs spider-entity`

## Development

### Running Tests
```bash
python -m pytest tests/test_spider.py -v
```

### Development Mode
```bash
python spider_entity.py --dev --debug
```

### Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.
