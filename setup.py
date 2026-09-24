from setuptools import setup, find_packages

setup(
    name="zap-job-hunter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "python-jobspy>=1.1.0",
        "pymupdf>=1.23.0",
        "scikit-learn>=1.3.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "pandas>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "zap-hunt=job_hunter.cli:main",
        ],
    },
    python_requires=">=3.10",
)
