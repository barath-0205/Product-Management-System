from setuptools import setup, find_packages

setup(
    name="product-management-system",
    version="0.1.0",
    packages=find_packages(),  # Automatically includes backend, frontend
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "aiohttp",
        "streamlit",
        "requests",
        "pydantic",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A FastAPI + Streamlit-based product management system",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
