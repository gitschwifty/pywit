# coding=utf-8
from setuptools import find_packages
from setuptools import setup

setup(
    name='pywit',
    version='0.2.0',
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
            'pywit=pywitness.cli:run_loop',
            'pywit_enable=pywitness.cli:enable',
            'pywit_status=pywitness.cli:status'
        ]
    })
