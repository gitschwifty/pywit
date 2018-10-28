from setuptools import find_packages
from setuptools import setup

setup(
    name='pywit',
    version='1.1.0',
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
        'cmd2',
    ],
    entry_points={
        'console_scripts': [
            'pywit=pywit.cli:pywit',
        ]
    })
