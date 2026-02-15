from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hybrid-vcs-core",
    version="1.0.0",
    author="Hybrid VCS Team",
    author_email="team@hybridvcs.io",
    description="A hybrid version control system combining centralized and distributed features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sashasmith-syber/hybrid-vcs-core-",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Flask>=3.0.0",
        "Werkzeug>=3.0.1",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
        "lxml>=5.1.0",
        "jinja2>=3.1.3",
        "click>=8.1.7",
        "gitpython>=3.1.40",
        "psutil>=5.9.6",
        "colorama>=0.4.6",
        "python-dotenv>=1.0.0",
        "watchdog>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "hybrid-vcs=app:main",
            "hvcs-quick-start=quick_start:main",
            "hvcs-status=show_status:main",
        ],
    },
)
