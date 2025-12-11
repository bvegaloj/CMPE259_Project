"""
Setup script for SJSU Virtual Assistant
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="sjsu-virtual-assistant",
    version="1.0.0",
    author="SJSU CMPE 259 Team",
    description="AI-powered virtual assistant for San Jose State University",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bvegaloj/CMPE259_Project",
    packages=find_packages(exclude=["tests", "tests.*", "docs", "scripts"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ],
        'docs': [
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'sjsu-assistant=src.main:main',
            'sjsu-demo=demo_agent:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.yaml', '*.json', '*.txt'],
    },
    zip_safe=False,
)
