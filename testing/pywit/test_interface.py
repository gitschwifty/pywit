from pywit.interface import SteemExplorer
from pywit.config import Configuration
from pywit.logger import Logger
import pytest

class TestInterface(object):
	def test_lock(self):
		conf = Configuration()
		log = Logger()
		stm = SteemExplorer(con=conf, log=log)
		assert stm.locked() == True
