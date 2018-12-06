pywit
********
pywit is a command line tool for steem, which is built using beem from holgern (holger80 on steem), and based off a similar tool built on steempy, conductor, built by Netherdrake.

Current Build Status
------------------
Version 1.0.0 has been released! This contains all of the features I originally intended to include in pywit.

As of right now, this has only been verifiably tested with Python 3.6.x. More will come, but it should run on anything above 3.4.x.

.. image:: https://circleci.com/gh/gitschwifty/pywit/tree/master.svg?style=svg
    :target: https://circleci.com/gh/gitschwifty/pywit/tree/master
.. image:: https://api.codeclimate.com/v1/badges/5f6eb763c21a40bb0d3a/maintainability
   :target: https://codeclimate.com/github/gitschwifty/pywit/maintainability
   :alt: Maintainability
.. image:: https://api.codeclimate.com/v1/badges/5f6eb763c21a40bb0d3a/test_coverage
   :target: https://codeclimate.com/github/gitschwifty/pywit/test_coverage
   :alt: Test Coverage

Dependencies
-------------------

Python 3.4.x+

Dependencies for beem (from holgern's README)

For Debian and Ubuntu:
::

    sudo apt-get install build-essential libssl-dev python-dev

For Fedora and RHEL-derivatives:
::

    sudo yum install gcc openssl-devel python-devel

For OSX:
::

    brew install openssl
    export CFLAGS="-I$(brew --prefix openssl)/include $CFLAGS"
    export LDFLAGS="-L$(brew --prefix openssl)/lib $LDFLAGS"

For Termux on Android (untested but if beem works on it this should):
::

    pkg install clang openssl-dev python-dev

For quicker signing and verifying:
::

    pip3 install -U cryptography

Dependencies for pywit

For auto-completion in the tool on OSX:
::

    pip3 install -U gnureadline

Installation
----------------

Install the latest version of pywit:
::

    pip3 install -U git+https://github.com/gitschwifty/pywit.git

Uses
=========

Running `pywit` by itself will get you an interactive command line session. The first time you open it up, it will run an initialization, getting your witness details and asking if you would like to set up a wallet. You should do this before attempting other commands, as most of them require the wallet and/or witness setup. Once in the interactive shell, use help and help $COMMAND to figure it out. Most command names are intuitive.

Options: -vv for level 2 verbosity, -vvv for level 3, the highest. Testing can be done with -t, no transactions will be broadcasted.
To enable verbosity or testing in the below commands, put the options between pywit and the subcommands:
::
  pywit -vvv feeds

Command Arguments
-------------------

Some commands can be run straight from the command line for ease of use. Options in parentheses are not required.

Feeds runs a price feed.
::
  pywit feeds (-w WAITTIME -s MIN_SPREAD -p PUBLISH_NOW)

Monitor monitors your witness, disabling or switching to a backup key at a certain number of missed blocks.
::
  pywit monitor (-b BACKUP_KEY -m MISSED_BLOCKS -w WAITTIME)

Enable enables your witness, either with a key passed or from your configuration file.
::
  pywit enable (-k KEY)

Disable disables your witness server.
::
  pywit disable

Status gets and prints your witness status.
::
  pywit status

Update runs through questions to update your witness information.
::
  pywit update

Please add any issues with errors, problems, or features you'd like to request
----------------------------------------------------------------------------------

Acknowledgements
===================

Thanks to holgern for creating beempy since steempy is apparently getting out-of-date, and Netherdrake for creating the original version of this tool.
