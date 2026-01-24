from setuptools import setup, find_packages

setup(
    name="a1-log-analyzer",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "analyze=cli.analyze:main",
        ]
    },
)
