from pywit.interface import SteemExplorer
from pywit.config import Configuration
from pywit.logger import Logger
import unittest

firstpass = "testtwothree"
secondpass = "testfourfive"

conf = Configuration()
log = Logger()
stm = SteemExplorer(con = conf, log = log, nobroadcast = True)

class TestInterface(unittest.TestCase):

	def test_wallet(self):
		stm.delete_wallet()
		stm.create_wallet(firstpass)
		self.assertTrue(stm.is_wallet())
		stm.unlock_wallet(firstpass)
		self.assertTrue(stm.unlocked())
		self.assertFalse(stm.locked())
		stm.lock_wallet()
		self.assertTrue(stm.locked())
		self.assertFalse(stm.unlocked())

	def test_change_passphrase(self):
		stm.unlock(firstpass)
		self.assertTrue(sstm.unlocked())
		self.assertFalse(stm.locked())
		stm.change_passphrase(secondpass)
		stm.lock()
		self.assertTrue(stm.locked())
		self.assertFalse(stm.unlocked())
		self.unlock(secondpass)
		self.assertTrue(stm.unlocked())
		stm.change_passphrase(firstpass)
		gstm.lock()
