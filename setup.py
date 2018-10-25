from setuptools import find_packages
from setuptools import setup

setup(
    name='pywit',
    version='1.0.2',
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
        'gnureadline',
    ],
    entry_points={
        'console_scripts': [
            'pywit=pywitness.cli:pywit',
        ]
    })
