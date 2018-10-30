from pywit.interface import SteemExplorer
from pywit.config import Configuration
from pywit.logger import Logger
import unittest

firstpass = "testtwothree"
secondpass = "testfourfive"

class TestInterface(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.conf = Configuration()
		cls.log = Logger()
		cls.stm = SteemExplorer(con=conf, log=log)
		cls.stm.delete_wallet(True)
		cls.stm.create_wallet(firstpass)
		cls.stm.unlock_wallet(firstpass)
		cls.stm.lock_wallet()

	def test_wallet(self):
		self.stm.lock_wallet()
		self.stm.unlock_wallet(firstpass)
		self.assertTrue(cls.stm.unlocked())
		self.assertFalse(cls.stm.locked())
		self.stm.lock_wallet()
		self.assertTrue(cls.stm.locked())
		self.assertFalse(cls.stm.unlocked())

	def test_change_passphrase(self):
		self.stm.unlock(firstpass)
		self.assertTrue(self.stm.unlocked())
		self.assertFalse(self.stm.locked())
		self.stm.change_passphrase(secondpass)
		self.stm.lock()
		self.assertTrue(self.stm.locked())
		self.assertFalse(self.stm.unlocked())
		self.unlock(secondpass)
		self.assertTrue(self.stm.unlocked())
		self.stm.change_passphrase(firstpass)
		self.stm.lock()
