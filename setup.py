from setuptools import setup, find_packages

requirements = [x.strip() for x in open("requirements.txt", "r").readlines()]

setup(
    name='0SINTr',
    version='0.1.0',
    description='Gathering data based on username or email address.',
    author='0SINTr',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            '0sintr = main:main'
        ]
    },
    python_requires='>=3.10',
)