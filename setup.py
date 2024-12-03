from setuptools import setup, find_packages
import os

# Check if requirements file exists
requirements_path = "requirements.txt"
if os.path.exists(requirements_path):
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = f.read().splitlines()
else:
    print(
        f"Warning: {requirements_path} does not exist. Defaulting to an empty list of requirements."
    )
    requirements = []

# Check if README.md exists
readme_path = "README.md"
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    print(
        f"Warning: {readme_path} does not exist. Defaulting to an empty long description."
    )
    long_description = ""

# Setup configuration
setup(
    name="etl_integrations_project_lydon",
    version="2.1.0",
    author="Lydon C*****",
    author_email="lydon******@gmail.com",
    description="As part of the Systems Integration Engineer project. Done in Q4 2024.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Future-proof URL (replace with actual repo)
    url="https://github.com/Lydon-01/",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md"],
    },
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
