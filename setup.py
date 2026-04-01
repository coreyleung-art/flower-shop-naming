#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
花店物品命名审查工具 - 安装配置
"""

from setuptools import setup, find_packages

setup(
    name="flower-shop-naming",
    version="2.0.0",
    author="Corey Leung",
    author_email="coreyleung@example.com",
    description="花店物品命名标准化CLI工具 - 将电商平台商品名称转换为标准命名格式",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/coreyleung-art/flower-shop-naming",
    license="MIT",
    py_modules=["item_naming_cli"],
    install_requires=[
        # 无外部依赖，纯Python标准库
    ],
    entry_points={
        "console_scripts": [
            "flower-naming=item_naming_cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    keywords="flower shop naming standard cli 花店 命名 标准化",
)
