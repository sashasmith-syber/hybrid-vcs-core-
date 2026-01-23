# Contributing to Hybrid VCS

Thank you for your interest in contributing to Hybrid VCS! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Git LFS (for handling large binary files)

### Setting up the Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/hybrid-vcs.git
   cd hybrid-vcs
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   make install-dev
   # or manually:
   pip install -e ".[dev,docs]"
   ```

4. **Verify installation:**
   ```bash
   make test
   ```

## Development Workflow

### Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run all formatting and linting:
```bash
make format
make lint
```

### Testing

We use pytest for testing. Tests are located in the `tests/` directory.

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run specific test file
pytest tests/test_core.py -v
```

### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write code following the existing style
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes:**
   ```bash
   make dev  # Runs format, lint, and test
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

5. **Push and create a pull request:**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Organization

```
hybrid-vcs-project/
├── hybrid_vcs/           # Main package
│   ├── __init__.py      # Package initialization
│   ├── core.py          # Main HybridVCS class
│   ├── git_manager.py   # Git operations
│   ├── database_manager.py  # SQLite operations
│   ├── compression.py   # Compression utilities
│   ├── config.py        # Configuration management
│   └── cli.py           # Command-line interface
├── tests/               # Test suite
├── examples/            # Usage examples
└── docs/               # Documentation
```

## Adding New Features

### Core Functionality

When adding new core functionality:

1. **Add the feature to the appropriate module:**
   - Git operations → `git_manager.py`
   - Database operations → `database_manager.py`
   - Compression → `compression.py`
   - Main API → `core.py`

2. **Add comprehensive tests:**
   - Unit tests for individual functions
   - Integration tests for workflows
   - Error handling tests

3. **Update the CLI if needed:**
   - Add new commands to `cli.py`
   - Update help text and documentation

4. **Add examples:**
   - Update existing examples or create new ones
   - Ensure examples work with the new feature

### Database Schema Changes

If you need to modify the database schema:

1. **Update the schema in `database_manager.py`**
2. **Add migration logic if needed**
3. **Update tests to handle schema changes**
4. **Document the changes in the changelog**

### Configuration Options

When adding new configuration options:

1. **Add to `config.py`**
2. **Update documentation**
3. **Add validation if needed**
4. **Update tests**

## Testing Guidelines

### Test Structure

- **Unit tests:** Test individual functions and methods
- **Integration tests:** Test complete workflows
- **Error handling:** Test error conditions and edge cases

### Test Naming

- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<functionality>`

### Test Data

- Use temporary directories for file operations
- Clean up test data in teardown methods
- Use fixtures for common test setup

### Example Test

```python
def test_save_state(self, vcs):
    """Test state saving functionality."""
    test_state = {"key": "value", "number": 42}
    vcs.save_state("test_key", test_state)
    
    loaded_state = vcs.load_state("test_key")
    assert loaded_state == test_state
```

## Documentation

### Code Documentation

- Use docstrings for all public functions and classes
- Follow Google-style docstring format
- Include type hints for all function parameters and return values

### README Updates

When adding features, update the README.md:
- Add to feature list
- Update usage examples
- Update API reference if needed

### Changelog

Update CHANGELOG.md with:
- New features
- Bug fixes
- Breaking changes
- Deprecations

## Pull Request Guidelines

### Before Submitting

1. **Ensure all tests pass:**
   ```bash
   make ci-test
   ```

2. **Update documentation**
3. **Add changelog entry**
4. **Rebase on latest main branch**

### Pull Request Description

Include in your PR description:
- **What:** Brief description of changes
- **Why:** Motivation for the changes
- **How:** Technical approach taken
- **Testing:** How you tested the changes
- **Breaking changes:** Any breaking changes

### Review Process

1. **Automated checks:** CI will run tests and linting
2. **Code review:** Maintainers will review your code
3. **Feedback:** Address any feedback from reviewers
4. **Merge:** Once approved, your PR will be merged

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR:** Breaking changes
- **MINOR:** New features (backward compatible)
- **PATCH:** Bug fixes (backward compatible)

### Release Checklist

1. Update version in `__init__.py` and `pyproject.toml`
2. Update CHANGELOG.md
3. Create release tag
4. Build and upload to PyPI
5. Create GitHub release

## Getting Help

### Communication

- **GitHub Issues:** Bug reports and feature requests
- **GitHub Discussions:** Questions and general discussion
- **Email:** contact@hybridvcs.com for private matters

### Resources

- **Documentation:** [Read the Docs](https://hybrid-vcs.readthedocs.io/)
- **Examples:** Check the `examples/` directory
- **Tests:** Look at existing tests for usage patterns

## Code of Conduct

### Our Standards

- **Be respectful:** Treat everyone with respect and kindness
- **Be inclusive:** Welcome contributors from all backgrounds
- **Be constructive:** Provide helpful feedback and suggestions
- **Be patient:** Remember that everyone is learning

### Reporting Issues

If you experience or witness unacceptable behavior, please report it to contact@hybridvcs.com.

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- GitHub contributors page

Thank you for contributing to Hybrid VCS!
