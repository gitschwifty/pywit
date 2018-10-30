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
	@classmethod
	def setUpClass(cls):
		cls.conf = Configuration()
		cls.log = Logger()
		cls.stm = SteemExplorer(con = cls.conf, log = cls.log, nobroadcast = True)
		cls.stm.delete_wallet()
		cls.stm.create_wallet(p = firstpass)

	def test_wallet_locks(self):
		self.stm.delete_wallet()
		self.assertFalse(self.stm.is_wallet())
		self.stm.create_wallet(p = firstpass)
		self.assertTrue(self.stm.is_wallet())
		self.stm.unlock_wallet(p = firstpass)
		self.assertTrue(self.stm.unlocked())
		self.assertFalse(self.stm.locked())
		self.stm.lock_wallet()
		self.assertTrue(self.stm.locked())
		self.assertFalse(self.stm.unlocked())

	def test_change_passphrase(self):
		self.stm.unlock(p = firstpass)
		self.assertTrue(self.stm.unlocked())
		self.assertFalse(self.stm.locked())
		self.stm.change_passphrase(p = secondpass)
		self.stm.lock()
		self.assertTrue(self.stm.locked())
		self.assertFalse(self.stm.unlocked())
		self.unlock(p = secondpass)
		self.assertTrue(self.stm.unlocked())
		self.stm.change_passphrase(p = firstpass)
		self.stm.lock()
