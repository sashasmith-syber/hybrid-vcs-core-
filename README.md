# Hybrid VCS Core

A modern, production-ready version control system combining centralized and distributed features with integrated web crawling capabilities.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-production-brightgreen.svg)](https://github.com/sashasmith-syber/hybrid-vcs-core-)

## 🌟 Features

- **Hybrid Architecture**: Combines the best of centralized (CVCS) and distributed (DVCS) version control
- **Web Interface**: Built-in Flask web server with RESTful API
- **Spider Entity**: Automated web crawler with version control integration
- **Branching & Merging**: Full support for branches and commit history
- **Hot Reload**: Development server with automatic restart on code changes
- **Production Ready**: Complete monitoring, status dashboard, and deployment tools

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Core Components](#-core-components)
- [Usage Examples](#-usage-examples)
- [API Reference](#-api-reference)
- [Architecture](#-architecture)
- [Spider Entity](#-spider-entity)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/sashasmith-syber/hybrid-vcs-core-.git
cd hybrid-vcs-core-

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

### Run the Demo

```bash
# Run the quick start demonstration
python quick_start.py

# Or in interactive mode
python quick_start.py --interactive
```

### Start the Web Server

```bash
# Production mode
python app.py

# Development mode with hot reload
python run_local.py
```

Access the web interface at `http://localhost:5000/`

## 📦 Installation

### Requirements

- Python 3.8 or higher
- pip (Python package manager)

### Install from PyPI (when published)

```bash
pip install hybrid-vcs-core
```

### Install from Source

```bash
git clone https://github.com/sashasmith-syber/hybrid-vcs-core-.git
cd hybrid-vcs-core-
pip install -e .
```

### Verify Installation

```bash
python -c "from hybrid_vcs_original import HybridVCS; print('Installation successful!')"
```

## 🔧 Core Components

### 1. Hybrid VCS Engine (`hybrid_vcs_original.py`)

The core version control system implementation:

```python
from hybrid_vcs_original import HybridVCS

# Initialize VCS
vcs = HybridVCS()

# Create a repository
vcs.init_repository("my-project")

# Add files
vcs.add_file("my-project", "README.md", b"# My Project")

# Commit changes
vcs.commit("my-project", "Initial commit", "John Doe")

# Create and switch branches
vcs.create_branch("my-project", "feature-branch")
vcs.checkout("my-project", "feature-branch")
```

### 2. Web Application (`app.py`)

Flask-based web interface with RESTful API:

```bash
# Start the server
python app.py

# Environment variables
export PORT=8080
export DEBUG=true
python app.py
```

### 3. Development Server (`run_local.py`)

Hot-reload development server:

```bash
# Start development server
python run_local.py

# Custom port
python run_local.py --port 8080

# Watch specific directories
python run_local.py --watch . ./modules
```

### 4. Spider Entity (`spider_entity.py`)

Web crawler with VCS integration:

```bash
# Crawl a website
python spider_entity.py https://example.com

# Custom configuration
python spider_entity.py https://example.com --config my_config.json --depth 3
```

### 5. Status Dashboard (`show_status.py`)

System monitoring and health checks:

```bash
# Display status
python show_status.py

# Export to JSON
python show_status.py --export status.json

# Watch mode (auto-refresh)
python show_status.py --watch
```

## 💡 Usage Examples

### Basic Repository Operations

```python
from hybrid_vcs_original import HybridVCS

vcs = HybridVCS()

# Initialize repository
result = vcs.init_repository("demo-repo")
print(result)

# Add multiple files
files = {
    "main.py": b"print('Hello, World!')",
    "README.md": b"# Demo Repository",
    "config.json": b'{"version": "1.0.0"}'
}

for filename, content in files.items():
    vcs.add_file("demo-repo", filename, content)

# Commit with message
vcs.commit("demo-repo", "Add initial files", "Developer")

# View history
history = vcs.get_history("demo-repo")
print(f"Total commits: {history['total']}")
```

### Web API Usage

```bash
# Initialize repository
curl -X POST http://localhost:5000/api/init \
  -H "Content-Type: application/json" \
  -d '{"name": "web-repo"}'

# Add file (base64 encoded)
curl -X POST http://localhost:5000/api/add \
  -H "Content-Type: application/json" \
  -d '{
    "repo": "web-repo",
    "file": "test.txt",
    "content": "SGVsbG8sIFdvcmxkIQ=="
  }'

# Commit changes
curl -X POST http://localhost:5000/api/commit \
  -H "Content-Type: application/json" \
  -d '{
    "repo": "web-repo",
    "message": "Add test file",
    "author": "API User"
  }'

# Get repository status
curl http://localhost:5000/api/status/web-repo
```

### Spider Crawling

```python
from spider_entity import SpiderEntity

# Initialize spider
spider = SpiderEntity(config_path="spider_config.json")

# Crawl website
result = spider.crawl("https://example.com", max_depth=2)

print(f"Pages crawled: {result['statistics']['pages_crawled']}")
print(f"Pages changed: {result['statistics']['pages_changed']}")

# View crawl history
history = spider.get_crawl_history()
```

## 🌐 API Reference

### Repository Management

- `POST /api/init` - Initialize a new repository
- `GET /api/repos` - List all repositories
- `GET /api/status/:repo` - Get repository status

### File Operations

- `POST /api/add` - Add file to staging area
- `POST /api/commit` - Commit staged changes
- `GET /api/history/:repo` - Get commit history

### Branch Operations

- `POST /api/branch` - Create a new branch
- `POST /api/checkout` - Switch to a branch

### Health & Monitoring

- `GET /health` - Service health check
- `GET /` - Web dashboard

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────┐
│           Web Interface (Flask)                  │
│                  app.py                          │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│         Core VCS Engine                          │
│      hybrid_vcs_original.py                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐│
│  │ Repository │  │  Commits   │  │  Branches  ││
│  │ Management │  │  & History │  │  & Merge   ││
│  └────────────┘  └────────────┘  └────────────┘│
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│        Storage Layer                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐│
│  │  Objects   │  │   Refs     │  │  Staging   ││
│  │   Store    │  │  & Tags    │  │    Area    ││
│  └────────────┘  └────────────┘  └────────────┘│
└─────────────────────────────────────────────────┘
```

### Component Interaction

```
Spider Entity ──┐
                ├──► Hybrid VCS ──► Repository Storage
Web API ────────┘           │
                            └──► Version History
                                      │
Quick Start ────────────────────────►│
CLI Tools ───────────────────────────┘
```

## 🕷️ Spider Entity

The Spider Entity is an intelligent web crawler that integrates seamlessly with the version control system.

### Features

- **Configurable Depth**: Control how deep the spider crawls
- **Domain Filtering**: Restrict crawling to specific domains
- **Rate Limiting**: Built-in delays to respect server resources
- **Change Detection**: Only commits when content changes
- **Version History**: Full history of webpage changes

### Configuration

Edit `spider_config.json`:

```json
{
  "max_depth": 2,
  "max_pages": 50,
  "delay_seconds": 1,
  "user_agent": "HybridVCS-Spider/1.0",
  "allowed_domains": ["example.com"],
  "exclude_patterns": ["/login", "/logout", ".pdf"],
  "timeout": 30
}
```

### Deployment

```bash
# Create a spider deployment
python deploy_spider.py create my-spider https://example.com

# Run the deployment
python deploy_spider.py run my-spider

# List all deployments
python deploy_spider.py list

# Get deployment status
python deploy_spider.py status my-spider
```

## 🔨 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/sashasmith-syber/hybrid-vcs-core-.git
cd hybrid-vcs-core-

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python run_local.py
```

### Project Structure

```
hybrid-vcs-core-/
├── app.py                    # Flask web application
├── hybrid_vcs_original.py    # Core VCS engine
├── spider_entity.py          # Web crawler
├── deploy_spider.py          # Spider orchestrator
├── run_local.py              # Development server
├── quick_start.py            # Demo script
├── show_status.py            # Status dashboard
├── spider_config.json        # Spider configuration
├── requirements.txt          # Python dependencies
├── setup.py                  # Package setup
├── pyproject.toml           # Modern Python config
├── .gitignore               # Git ignore patterns
└── README.md                # This file
```

### Running Tests

```bash
# Run quick start demo (validates core functionality)
python quick_start.py

# Check system status
python show_status.py

# Verify web server
python app.py &
curl http://localhost:5000/health
```

## 📚 Documentation

- [Quick Start Guide](README.md#-quick-start)
- [API Reference](README.md#-api-reference)
- [Architecture Overview](README.md#-architecture)
- [Spider Entity Guide](README.md#-spider-entity)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [Release Notes](RELEASE_NOTES.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by Git, Mercurial, and other version control systems
- Built with Flask for the web interface
- Uses Beautiful Soup for web scraping
- Colorama for terminal colors

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/sashasmith-syber/hybrid-vcs-core-/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sashasmith-syber/hybrid-vcs-core-/discussions)
- **Email**: team@hybridvcs.io

## 🗺️ Roadmap

- [ ] Add merge conflict resolution
- [ ] Implement remote repository sync
- [ ] Add webhook support for CI/CD
- [ ] Create GUI desktop application
- [ ] Add support for binary file diffing
- [ ] Implement repository cloning
- [ ] Add authentication and authorization

---

Made with ❤️ by the Hybrid VCS Team
