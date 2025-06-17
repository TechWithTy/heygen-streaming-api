from setuptools import setup, find_packages

setup(
    name="heygen-streaming",
    version="0.1.0",
    packages=find_packages(include=["heygen_streaming*"]),
    install_requires=[
        "httpx>=0.24.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.10.0",
            "pytest-cov>=4.0.0",
        ],
    },
    python_requires=">=3.8",
)
