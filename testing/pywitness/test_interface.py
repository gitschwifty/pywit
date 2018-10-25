from pywit.interface import SteemExplorer
from pywit.config import Configuration
from pywit.logger import Logger
import pytest


def test_stm_lock():
    conf = Configuration()
    log = Logger()
    stm = SteemExplorer(con=conf, log=log)
    assert stm.locked() == True
