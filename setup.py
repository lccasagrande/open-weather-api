import os

import pkg_resources
from setuptools import find_packages, setup

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "api", "__version__.py")) as f:
    exec(f.read(), about)


with open(os.path.join(here, "requirements.txt")) as f:
    install_requires = [str(req) for req in pkg_resources.parse_requirements(f)]

with open(os.path.join(here, "README.md")) as f:
    readme = f.read()

extras = {
    "test": [
        "black",
        "coverage",
        "flake8",
        "pydocstyle",
        "pytest",
        "pytest-asyncio",
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
    install_requires=install_requires,
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
