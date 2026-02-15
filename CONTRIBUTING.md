# Contributing to Hybrid VCS Core

Thank you for your interest in contributing to Hybrid VCS Core! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Community](#community)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, gender, gender identity and expression, sexual orientation, disability, personal appearance, body size, race, ethnicity, age, religion, or nationality.

### Expected Behavior

- Be respectful and considerate
- Welcome newcomers and help them get started
- Be collaborative and constructive in feedback
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, trolling, or discriminatory language
- Personal attacks or insults
- Publishing others' private information
- Other conduct which could reasonably be considered inappropriate

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of version control systems
- Familiarity with Python and Flask (for web components)

### First-Time Contributors

If you're new to open source, here are some good first steps:

1. Star and watch the repository to stay updated
2. Read through the README and documentation
3. Run the quick start demo to understand the system
4. Look for issues labeled `good-first-issue` or `help-wanted`
5. Join our community discussions

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/hybrid-vcs-core-.git
cd hybrid-vcs-core-

# Add upstream remote
git remote add upstream https://github.com/sashasmith-syber/hybrid-vcs-core-.git
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### 4. Verify Setup

```bash
# Run quick start demo
python quick_start.py

# Start development server
python run_local.py

# Check status
python show_status.py
```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

1. **Bug Fixes**: Fix issues found in the codebase
2. **Feature Development**: Implement new features from the roadmap
3. **Documentation**: Improve or expand documentation
4. **Testing**: Add or improve test coverage
5. **Performance**: Optimize existing code
6. **Examples**: Add usage examples or tutorials
7. **Design**: Improve UI/UX of web interface

### Contribution Workflow

1. **Find or Create an Issue**
   - Check existing issues for what you want to work on
   - If no issue exists, create one to discuss your idea
   - Wait for maintainer approval before starting major work

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

3. **Make Your Changes**
   - Write clean, readable code
   - Follow the coding standards (see below)
   - Add comments where necessary
   - Update documentation if needed

4. **Test Your Changes**
   - Run the quick start demo
   - Test affected functionality manually
   - Ensure no regressions

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

6. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a pull request on GitHub.

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line Length**: Maximum 100 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings (unless single quotes avoid escaping)
- **Docstrings**: Use triple double-quotes with Google style

### Code Structure

```python
"""
Module docstring explaining the purpose.

More detailed information if needed.
"""

import standard_library
import third_party
from local_module import something


class MyClass:
    """Class docstring explaining what this class does."""
    
    def __init__(self, param: str):
        """
        Initialize the class.
        
        Args:
            param: Description of parameter
        """
        self.param = param
    
    def my_method(self) -> str:
        """
        Method docstring.
        
        Returns:
            Description of return value
        """
        return self.param


def my_function(arg1: int, arg2: str) -> bool:
    """
    Function docstring.
    
    Args:
        arg1: Description
        arg2: Description
        
    Returns:
        Description of return value
    """
    return True
```

### Type Hints

Use type hints for function parameters and return values:

```python
from typing import Dict, List, Optional, Any

def process_data(data: Dict[str, Any], limit: Optional[int] = None) -> List[str]:
    """Process data and return results."""
    pass
```

### Error Handling

Always handle errors gracefully:

```python
try:
    result = risky_operation()
except SpecificException as e:
    print(f"Error: {str(e)}")
    return {"error": str(e)}
```

### Naming Conventions

- **Variables/Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`

## Testing Guidelines

### Manual Testing

For now, we primarily use manual testing:

1. **Quick Start Demo**: Must pass without errors
   ```bash
   python quick_start.py
   ```

2. **Web Server**: Must start and serve requests
   ```bash
   python app.py
   # Test in browser: http://localhost:5000
   ```

3. **Spider Crawling**: Must crawl and commit successfully
   ```bash
   python spider_entity.py https://example.com
   ```

4. **Status Dashboard**: Must display system information
   ```bash
   python show_status.py
   ```

### Future: Automated Tests

We plan to add automated tests in future versions. When contributing test-related code:

- Use `pytest` framework
- Aim for high coverage (>80%)
- Include both unit and integration tests
- Mock external dependencies

## Pull Request Process

### Before Submitting

- [ ] Code follows the style guidelines
- [ ] All existing functionality still works
- [ ] Documentation is updated if needed
- [ ] Commit messages are clear and descriptive
- [ ] No sensitive data or credentials in code

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other (please describe)

## Testing Performed
- [ ] Quick start demo
- [ ] Web server functionality
- [ ] Spider operations
- [ ] Status dashboard
- [ ] Other (please describe)

## Related Issues
Fixes #123

## Screenshots (if applicable)
[Add screenshots here]

## Additional Notes
Any additional information
```

### Review Process

1. A maintainer will review your PR within 1-3 business days
2. They may request changes or ask questions
3. Address feedback by pushing new commits to your branch
4. Once approved, a maintainer will merge your PR
5. Your contribution will be included in the next release

### After Merge

- Your changes will be in the `main` branch
- You'll be added to the contributors list
- Delete your feature branch (optional)
- Sync your fork with upstream

## Issue Reporting

### Before Creating an Issue

1. Search existing issues to avoid duplicates
2. Check if the issue is already fixed in `main`
3. Gather relevant information (version, OS, error messages)

### Bug Reports

Use this template:

```markdown
**Describe the Bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. Navigate to '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python Version: [e.g., 3.10.5]
- Hybrid VCS Version: [e.g., 1.0.0]

**Additional Context**
Any other relevant information.
```

### Feature Requests

Use this template:

```markdown
**Feature Description**
Clear description of the feature.

**Use Case**
Why is this feature needed? What problem does it solve?

**Proposed Solution**
Your ideas on how to implement it.

**Alternatives Considered**
Other approaches you've thought about.

**Additional Context**
Any other relevant information.
```

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions, ideas, and general discussion
- **Email**: team@hybridvcs.io for private inquiries

### Getting Help

If you need help:

1. Check the documentation first
2. Search existing issues and discussions
3. Ask in GitHub Discussions
4. Be patient and respectful

### Recognition

Contributors are recognized in several ways:

- Listed in release notes
- Mentioned in commit messages
- Added to contributors section
- Featured in project announcements

## License

By contributing to Hybrid VCS Core, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Hybrid VCS Core! Every contribution, no matter how small, helps make this project better. 🎉
