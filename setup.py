from setuptools import setup, find_packages

requirements = [x.strip() for x in open("requirements.txt", "r").readlines()]

setup(
    name='osintr',
    version='0.3.0',
    author='0SINTr',
    url='https://github.com/0SINTr',
    description='OFM - Stage 1 tool for GRASS (Google Recursive Advanced Search & Scrape).',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(include=['osintr', 'osintr.*']),
    install_requires=requirements,
    include_package_data=True,
    package_data={
        'osintr.templates': ['*.html'],
    },
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