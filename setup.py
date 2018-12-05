from setuptools import find_packages
from setuptools import setup

setup(
    name='pywit',
    version='1.2.0',
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
        'websocket-client',
        'pycryptodomex',
        'future',
        'Events',
        'ecdsa',
        'scrypt',
        'future',
        'pytz',
        'pylibscrypt',
    ],
    entry_points={
        'console_scripts': [
            'pywit=pywit.cli:pywit',
        ]
    })
