from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="text-generator",
    author="kelvin",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where=text-generator)
)