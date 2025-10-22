#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MLA V3 - Multi-Level Agent System
安装配置
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取 README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

# 读取依赖
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split('\n')
else:
    requirements = [
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.0.0",
        "requests>=2.31.0",
        "pyyaml>=6.0.0",
        "litellm>=1.0.0",
        "tiktoken>=0.5.0",
        "crawl4ai>=0.3.0",
        "ddgs>=1.0.0",
        "arxiv>=2.0.0",
        "pdfplumber>=0.10.0",
        "python-docx>=1.1.0",
        "chardet>=5.2.0",
        "prompt_toolkit>=3.0.0",
    ]

setup(
    name="mla-agent",
    version="3.0.0",
    author="Chenglin Yu",
    author_email="yuchenglin96@qq.com",
    description="Multi-Level Agent System for complex task automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mla-agent",
    packages=find_packages(exclude=['test*', 'task_*', 'conversations']),
    include_package_data=True,
    package_data={
        'MLA_V3': [
            'config/**/*.yaml',
            'tool_server_lite/**/*.py',
            'tool_server_lite/**/*.md',
            'tool_server_lite/requirements.txt',
        ],
    },
    install_requires=requirements,
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            'mla-agent=start:main',
            'mla-tool-server=tool_server_lite.server:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)

