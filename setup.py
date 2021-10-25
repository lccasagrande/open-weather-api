import os

from setuptools import find_packages, setup

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "api", "__version__.py")) as f:
    exec(f.read(), about)


with open("README.md", "r") as f:
    readme = f.read()


required_packages = []

extras = {
    "test": [
        "black",
        "coverage",
        "flake8",
        "pydocstyle",
        "pytest",
        "pytest-mock",
        "pytest-cov",
        "tox",
    ]
}


setup(
    packages=find_packages(exclude=("docs", "tests")),
    name=about["__title__"],
    description=about["__description__"],
    version=about["__version__"],
    author=about["__author__"],
    author_email=["__author_email__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    license=about["__license__"],
    python_requires=">=3.8",
    install_requires=required_packages,
    extras_require=extras,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
)
