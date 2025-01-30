from setuptools import setup, find_packages

__version__ = "0.0.1"

setup(
    name="celegans_connectome_analysis",
    version=__version__,
    packages=["celegans_connectome_analysis"],
    author="Thomas Athey",
    author_email="tom.l.athey@gmail.com",
    install_requires=[
        "pandas",
        "networkx",
        "matplotlib",
        "graspologic",
        "future",
        "openpyxl",
    ],
    license="MIT",
)