# Hybrid VCS

A powerful version control system that combines Git with SQLite for comprehensive state management, featuring Zstandard compression and parallel processing capabilities.

## Features

- **Hybrid Architecture**: Combines Git for file versioning with SQLite for state and configuration management
- **High-Performance Compression**: Uses Zstandard compression for efficient binary file storage
- **Parallel Processing**: Multi-threaded compression and processing for improved performance
- **Git LFS Integration**: Seamless handling of large binary files
- **State Management**: Persistent storage of application states and configurations
- **Telemetry & Feedback**: Built-in feedback recording system linked to Git commits
- **Branch Support**: Full Git branching capabilities
- **CLI Interface**: Comprehensive command-line interface for all operations
- **Connection Pooling**: Efficient SQLite connection management

## Installation

### From Source

```bash
git clone https://github.com/your-org/hybrid-vcs.git
cd hybrid-vcs
pip install -r requirements.txt
pip install -e .
```

### Using pip (when published)

```bash
pip install hybrid-vcs
```

## Quick Start

### Python API

```python
from hybrid_vcs import HybridVCS

# Initialize
vcs = HybridVCS()

# Create a branch
vcs.create_branch("development")

# Save files
commit_hash = vcs.save_version(["model.bin", "config.json"], "Initial version")

# Save application state
vcs.save_state("training_config", {
    "learning_rate": 0.001,
    "epochs": 100,
    "batch_size": 32
})

# Record feedback
vcs.record_feedback(
    severity=8,
    category="training",
    params={"accuracy": 0.95, "loss": 0.05},
    commit_hash=commit_hash
)

# Load state
config = vcs.load_state("training_config")

# Retrieve versioned files
files_data = vcs.get_version(commit_hash)
```

### Command Line Interface

```bash
# Initialize repository
hybrid-vcs init

# Save files
hybrid-vcs save model1.bin model2.bin -m "Initial model versions"

# Save state
hybrid-vcs state-save training_config -d '{"lr": 0.001, "epochs": 100}'

# Load state
hybrid-vcs state-load training_config

# Record feedback
hybrid-vcs feedback 8 training -p '{"accuracy": 0.95}' -c abc123

# Branch operations
hybrid-vcs branch create feature-branch
hybrid-vcs branch switch main
hybrid-vcs branch list

# Show status
hybrid-vcs status
```

## Architecture

### Core Components

1. **HybridVCS**: Main interface combining all functionality
2. **GitManager**: Handles Git operations with LFS support
3. **DatabaseManager**: Manages SQLite operations with connection pooling
4. **Compression**: Zstandard compression utilities
5. **CLI**: Command-line interface

### Data Flow

```
Files → Compression → Git LFS → Git Repository
                                      ↓
State/Config → JSON → SQLite Database ←
                                      ↓
Feedback/Telemetry → SQLite Database ←
```

## Configuration

Default configuration can be customized:

```python
from hybrid_vcs import HybridVCS, CONFIG

# Customize configuration
custom_config = CONFIG.copy()
custom_config.update({
    "REPO_DIR": "/path/to/custom/repo",
    "ZSTD_LEVEL": 9,  # Higher compression
    "MAX_WORKERS": 8,  # More parallel workers
})

vcs = HybridVCS(custom_config)
```

### Configuration Options

- `REPO_DIR`: Repository directory path
- `STATE_DB`: SQLite database filename
- `BINARY_DIR`: Directory for compressed binaries
- `ZSTD_LEVEL`: Compression level (1-22)
- `MAX_STATE_SIZE`: Maximum state size (bytes)
- `MAX_WORKERS`: Number of parallel workers

## Examples

### Basic Usage

See `examples/basic_usage.py` for a complete basic example:

```bash
cd examples
python basic_usage.py
```

### Advanced Usage

See `examples/advanced_usage.py` for parallel processing and branching:

```bash
cd examples
python advanced_usage.py
```

## Use Cases

### Machine Learning

- **Model Versioning**: Track different model checkpoints
- **Experiment Management**: Manage multiple training experiments
- **Configuration Tracking**: Store hyperparameters and training configs
- **Performance Monitoring**: Record training metrics and feedback

### Data Science

- **Dataset Versioning**: Version large datasets with compression
- **Pipeline States**: Track data processing pipeline states
- **Result Tracking**: Store analysis results and metadata

### Software Development

- **Asset Management**: Version large binary assets
- **Configuration Management**: Track application configurations
- **Release Management**: Manage release states and metadata

## API Reference

### HybridVCS Class

#### Methods

- `save_version(file_paths, message)`: Save files to version control
- `save_state(key, value)`: Save application state
- `load_state(key)`: Load application state
- `record_feedback(severity, category, params, commit_hash)`: Record feedback
- `get_version(commit_hash)`: Retrieve versioned files
- `create_branch(branch_name)`: Create new branch
- `switch_branch(branch_name)`: Switch to branch
- `get_status()`: Get repository status

## Development

### Setup Development Environment

```bash
git clone https://github.com/your-org/hybrid-vcs.git
cd hybrid-vcs
pip install -r requirements.txt
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/ -v --cov=hybrid_vcs
```

### Code Formatting

```bash
black hybrid_vcs/
flake8 hybrid_vcs/
mypy hybrid_vcs/
```

## Performance

### Compression Ratios

Typical compression ratios with Zstandard:
- Binary models: 2-5x compression
- Text configurations: 3-10x compression
- Mixed datasets: 2-8x compression

### Parallel Processing

- Multi-threaded compression for large files
- Configurable worker pool size
- Efficient for batch operations

## Limitations

- Requires Git and Git LFS for full functionality
- SQLite limitations apply to state storage
- File size limits configurable but recommended < 100MB per file
- Python 3.8+ required

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- GitHub Issues: [Report bugs and request features](https://github.com/your-org/hybrid-vcs/issues)
- Documentation: [Read the docs](https://hybrid-vcs.readthedocs.io/)
- Email: contact@hybridvcs.com

## Changelog

### v1.0.0
- Initial release
- Core VCS functionality
- Git integration with LFS
- SQLite state management
- Zstandard compression
- CLI interface
- Parallel processing
- Connection pooling
