"""
Setup script for Hybrid VCS package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Hybrid VCS - A version control system combining Git with SQLite for state management."

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-'):
                    # Extract just the package name and version, ignore comments
                    req = line.split('#')[0].strip()
                    if req:
                        requirements.append(req)
    return requirements

setup(
    name="hybrid-vcs",
    version="1.0.0",
    author="Hybrid VCS Team",
    author_email="contact@hybridvcs.com",
    description="A version control system combining Git with SQLite for state management",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/hybrid-vcs",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Version Control",
        "Topic :: Database",
        "Topic :: System :: Archiving :: Compression",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "docs": [
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "hybrid-vcs=hybrid_vcs.cli:main",
            "hvcs=hybrid_vcs.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="version-control git sqlite compression zstandard vcs",
    project_urls={
        "Bug Reports": "https://github.com/your-org/hybrid-vcs/issues",
        "Source": "https://github.com/your-org/hybrid-vcs",
        "Documentation": "https://hybrid-vcs.readthedocs.io/",
    },
)
