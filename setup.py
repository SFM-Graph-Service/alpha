from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="SFM-Graph-Service",
    version="1.0.0",
    description="A Social Fabric Matrix framework for modeling and analyzing complex socio-economic systems through graph-based data structures.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="SFM Graph Service Team",
    author_email="contact@example.com",
    url="https://github.com/SFM-Graph-Service/alpha",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.9",
    keywords="social-fabric-matrix, graph-analysis, policy-analysis, network-analysis",
)
