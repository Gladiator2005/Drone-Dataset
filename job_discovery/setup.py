"""
Setup script for job discovery system.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="job-discovery",
    version="1.0.0",
    author="Job Discovery Team",
    description="AI/ML Internship and Entry-Level Job Discovery System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Gladiator2005/Drone-Dataset",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "job-discovery=job_discovery.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "job_discovery": ["config.yaml"],
    },
)
