from setuptools import setup, find_packages

requirements = [x.strip() for x in open("requirements.txt", "r").readlines()]

setup(
    name='osintr',
    version='0.2.0',
    description='Gathering open-source data on target based on user input.',
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
    ],  
    python_requires='>=3.12',
)