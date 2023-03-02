import re

from setuptools import find_packages, setup

NAME = "ezyquant-execution"

VERSIONFILE = "ezyquant_execution/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

setup(
    name=NAME,
    packages=find_packages(include=["ezyquant_execution", "ezyquant_execution.*"]),
    version=verstr,
    description="Ezyquant execution",
    long_description="Ezyquant execution",
    author="Fintech (Thailand) Company Limited",
    author_email="admin@fintech.co.th",
    url="https://pydoc.ezyquant.com/",
    maintainer="Fintech (Thailand) Company Limited",
    maintainer_email="admin@fintech.co.th",
    python_requires=">=3.8",
    install_requires=["pandas>=1.3", "settrade-v2>=2.1,<2.2"],
    license="The MIT License (MIT)",
    classifiers=[
        "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    project_urls={
        "Documentation": "https://pydoc.ezyquant.com/",
        "Bug Reports": "https://github.com/ezyquant/ezyquant-execution/issues",
        "Source": "https://github.com/ezyquant/ezyquant-execution",
    },
)
