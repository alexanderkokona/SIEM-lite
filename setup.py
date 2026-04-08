"""
setup.py

Package configuration for SIEM-lite
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="SIEM-lite",
    version="0.1.0",
    author="SIEM-lite Contributors",
    description="A small, disciplined security log pipeline for Linux authentication events",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/SIEM-lite",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: No Input/Output (Daemon)",
        "Topic :: System :: Monitoring",
        "Topic :: Security",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "siem-lite-verify=scripts.verify_auth_log_access:main",
        ],
    },
    include_package_data=True,
)
