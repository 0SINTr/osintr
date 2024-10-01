from setuptools import setup, find_packages

requirements = [x.strip() for x in open("requirements.txt", "r").readlines()]

setup(
    name='osintr',
    version='0.3.0',
    description='OFM Stage 1 tool for GRASS (Google Recursive Advanced Search & Scrape).',
    author='0SINTr',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'osintr = osintr.main:main'
        ]
    },
    classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    ]
)