from setuptools import setup, find_packages

setup(
    name="agent-management-mcp",
    version="1.0.0",
    description="MCP Server for Agent Management Platform",
    author="Agent Management Platform",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "mcp>=0.9.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "python-dotenv>=1.0.0",
        "aiofiles>=23.0.0",
        "anthropic>=0.18.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
        ]
    },
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "agent-mcp=agent_mcp.server:main",
        ],
    },
)
