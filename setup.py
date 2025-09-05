"""Setup script for card-collector package."""
from setuptools import setup, find_packages

# Read dependencies from requirements.txt if it exists, otherwise define them here
dependencies = [
    "discord.py>=2.3.0",
    "fastapi>=0.104.0", 
    "uvicorn[standard]>=0.24.0",
    "sqlalchemy>=2.0.0",
    "alembic>=1.12.0",
    "psycopg[binary]>=3.1.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "apscheduler>=3.10.0",
    "jinja2>=3.1.0",
    "python-multipart>=0.0.6",
    "httpx>=0.25.0",
    "pillow>=10.0.0",
    "python-jose[cryptography]>=3.3.0",
    "aiosqlite>=0.19.0",
]

dev_dependencies = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]

setup(
    name="card-collector",
    version="0.1.0",
    description="Discord bot for collectible card management",
    long_description="A comprehensive Discord bot for managing collectible cards with web interface",
    long_description_content_type="text/plain",
    author="Card Collector",
    author_email="cards@example.com",
    python_requires=">=3.11",
    packages=find_packages(),
    install_requires=dependencies,
    extras_require={
        "dev": dev_dependencies,
    },
    entry_points={
        "console_scripts": [
            "card-bot=bot.main:main",
            "card-web=web.app:main", 
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)