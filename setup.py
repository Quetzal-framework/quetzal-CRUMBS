import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="quetzal-crumbs",
    version="0.0.2",
    description='Utility scripts for Quetzal-based programs',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/Becheler/quetzal-CRUMBS',
    author='Arnaud Becheler',
    author_email='arnaud.becheler@gmail.com',
    packages=["crumbs"],
    include_package_data=True
    install_requires=[
        'numpy',
        'GDAL',
        'pyvolve'
    ]
)
