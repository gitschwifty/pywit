# coding=utf-8
from setuptools import find_packages
from setuptools import setup

setup(
    name='pywallet',
    version='0.1.0',
    description='Steem Python Witness Toolkit',
    packages=find_packages(),
    setup_requires=['pytest-runner'],
    tests_require=['pytest',
                   'pytest-pylint',
                   'pytest-console-scripts'],
    install_requires=[
        'Click',
        'click-spinner',
        'requests',
        'prettytable',
        'beem',
    ],
    entry_points={
        'console_scripts': [
            'pywallet=pywitness.cli:run_loop',
        ]
    })
