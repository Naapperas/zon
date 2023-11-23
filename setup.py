import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Naapperas",  # Replace with your username
    version="0.0.1",
    author="Naapperas",
    author_email="nunoafonso2002@gmail.com",
    description="A Zod-like validation library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/naapperas/pod",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)
