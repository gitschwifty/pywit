from pywit.interface import SteemExplorer
from pywit.config import Configuration
from pywit.logger import Logger
import unittest
import tempfile
import os
from unittest import mock
from beem.exceptions import (
    WrongMasterPasswordException,
    AccountDoesNotExistsException,
    MissingKeyError,
    NoWalletException,
)
from beemgraphenebase.account import (
    PrivateKey,
    PublicKey,
)

firstpass = "testtwothree"
secondpass = "testfourfive"
fakename = "testetsstst1235asdkfj"
realacc = "petertag"
realsig = "STM7fKCoLs5wiTchPLaiRPPXo1NfPTYDqvAYoPgF3mWK2mpEzLDz5"
brain = "HIGUERO KHANKAH LA BITTER BABBLER INLYING GAN SECALIN PREBORN DROME PEDRAIL CRANIC TABORET PUNNIC FLOEY WAXER"
privkey = "5JbM6ziPqAtsMeWy6uKfC4PQWqkehkjaWTr5qbUrE8HW8mdaP24"
pubkey = "STM6PfdHebimMt1LkRPzy3JyBqXeWUj1XoQzNNuuTuym92WBNaT6i"
wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"
tmpconf = tempfile.mkstemp()
os.remove(tmpconf[1])


class TestInterface(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conf = Configuration(tmpconf[1])
        cls.conf.check_config(realacc)
        cls.log = Logger()
        cls.stm = SteemExplorer(con = cls.conf, log = cls.log,
                                nobroadcast = True)
        #recreate cls.stm when testing with passed key, passing the key in
        #constructor
        cls.stm.delete_wallet()
        cls.stm.create_wallet(firstpass)
        cls.stm.lock()

    @classmethod
    def tearDownClass(cls):
        cls.conf.delete_config()
        cls.stm.delete_wallet()

    @mock.patch('getpass.getpass')
    def test_missing_key(self, gp):
        # Delete wallet and remove keys from stm
        self.stm = SteemExplorer(con = self.conf, log = self.log,
                                nobroadcast = False)

        gp.return_value = firstpass
        self.assertRaises(MissingKeyError, self.stm.update)

        self.stm = SteemExplorer(con = self.conf, log = self.log,
                                nobroadcast = True)
        self.stm.lock()

    def test_wallet_existence(self):
        # Delete wallet to ensure delete works
        self.stm.delete_wallet()
        self.assertFalse(self.stm.is_wallet())

        # Create new wallet and ensure it is unlocked after creation
        self.stm.create_wallet(p=firstpass)
        self.assertTrue(self.stm.is_wallet())
        self.assertTrue(self.stm.unlocked())

        # Lock wallet for other testing
        self.stm.lock_wallet()

    def test_wallet_locks(self):
        # Lock wallet and check lock
        self.stm.lock_wallet()
        self.assertTrue(self.stm.locked())
        self.assertFalse(self.stm.unlocked())

        # Unlock wallet, check unlock with incorrect password, and check locks
        self.assertFalse(self.stm.unlock_wallet(secondpass))
        self.assertTrue(self.stm.unlock_wallet(firstpass))
        self.assertTrue(self.stm.unlocked())
        self.assertFalse(self.stm.locked())

        # Relock wallet and check lock and unlock aliases
        self.stm.lock()
        self.assertTrue(self.stm.locked())
        self.assertFalse(self.stm.unlock(secondpass))
        self.assertTrue(self.stm.unlock(firstpass))
        self.assertTrue(self.stm.unlocked())

        # Lock wallet for other testing
        self.stm.lock_wallet()

    def test_change_passphrase(self):
        # Unlock and change passphrase from first to secondpass
        self.stm.unlock(firstpass)
        self.stm.change_passphrase(secondpass)
        self.stm.lock()

        # Make sure firstpass no longer unlocks the wallet
        self.assertFalse(self.stm.unlock(firstpass))
        self.assertTrue(self.stm.locked())

        # Make sure secondpass unlocks wallet now
        self.assertTrue(self.stm.unlock(secondpass))
        self.assertTrue(self.stm.unlocked())

        # Change passphrase back to firstpass
        self.stm.change_passphrase(p=firstpass)

        # Lock for other testing
        self.stm.lock()

    @mock.patch('getpass.getpass')
    def test_getpass(self, gp):
        # Delete wallet and check input on create_wallet
        self.stm.delete_wallet()
        gp.return_value = firstpass
        self.assertTrue(self.stm.create_wallet())
        self.assertTrue(self.stm.is_wallet())

        # Check input on unlock and ensure password is correct
        self.assertTrue(self.stm.unlock_wallet())
        self.assertTrue(self.stm.unlocked())

        # Make sure incorrect input does not unlock
        gp.return_value = secondpass
        self.stm.lock_wallet()
        self.assertFalse(self.stm.unlock_wallet())
        self.assertTrue(self.stm.locked())

        # Check unlock failure in change passphrase
        self.assertFalse(self.stm.change_passphrase())

        # Unlock and check input on change passphrase
        self.stm.unlock_wallet(firstpass)
        self.assertTrue(self.stm.change_passphrase())
        self.stm.lock_wallet()

        # Make sure new passphrase works
        self.assertTrue(self.stm.unlock_wallet())
        self.assertTrue(self.stm.unlocked())

        # Check unlock success in change passphrase & return to firstpass
        self.stm.lock()
        self.assertTrue(self.stm.change_passphrase(firstpass))

        # Lock for other testing
        self.stm.lock()

    def test_change_broadcast(self):
        # Make sure nobroadcast is true, change it to false, check, then change
        # back to true
        self.assertTrue(self.stm.stm.nobroadcast)
        self.stm.change_broadcast(False)
        self.assertFalse(self.stm.stm.nobroadcast)
        self.stm.change_broadcast(True)
        self.assertTrue(self.stm.stm.nobroadcast)
        self.stm = SteemExplorer(con = self.conf, log = self.log,
                                nobroadcast = True)

    def test_cost_compute(self):
        # Test all RC costs with default function values against previously
        # recorded low cost transaction values.

        # Comments
        c = self.stm.compute_cost(type=1)
        self.assertTrue(c >= 1091365993)

        # Votes
        c = self.stm.compute_cost(type=2)
        self.assertTrue(c >= 245894621)

        # Transfer
        c = self.stm.compute_cost(type=3)
        self.assertTrue(c >= 3594717)

        # Custom Json
        c = self.stm.compute_cost(type=4)
        self.assertTrue(c >= 3594720)

        # Incorrect type
        c = self.stm.compute_cost(type=5)
        self.assertFalse(c)

    @mock.patch('getpass.getpass')
    def test_add_key(self, gp):
        # Tests all cases of adding a private key to wallet
        # Test no key passed
        self.assertFalse(self.stm.add_key(''))

        # Test no wallet
        self.stm.delete_wallet()
        self.assertFalse(self.stm.add_key(privkey))

        # Test wallet locked
        gp.return_value = firstpass
        self.stm.create_wallet()
        self.assertTrue(self.stm.add_key(privkey))

        # Test unlock failure
        gp.return_value = secondpass
        self.stm.lock()
        self.assertFalse(self.stm.add_key(privkey))

    def test_get_rc(self):
        # Tests all cases of the get rc function
        # Real account name
        m = self.stm.get_rc(realacc)
        self.assertTrue(m['current_mana'] > 0)
        self.assertTrue(m['max_mana'] >= m['current_mana'])
        self.assertTrue(m['current_pct'] > 0)

        # Incorrect account name
        self.assertRaises(AccountDoesNotExistsException,
                          self.stm.get_rc, fakename)

    def test_witness_json(self):
        # Tests witness json
        w = self.stm.witness_json(realacc)
        self.assertTrue(w['id'] == 14793)
        self.assertTrue(w['owner'] == 'petertag')

        w = self.stm.witness_json(fakename)
        self.assertFalse(w)

    def test_check_key(self):
        # Tests key checker
        # real account, correct key
        self.assertTrue(self.stm.check_key(realacc, realsig))

        # real account, wrong key
        self.assertFalse(self.stm.check_key(realacc, pubkey))

        # fake account
        self.assertFalse(self.stm.check_key(fakename, pubkey))

    @mock.patch('getpass.getpass')
    def test_disable_and_update(self, gp):
        # Tests witness disabler and update methods - no broadcasting
        gp.return_value = firstpass

        # Test disable
        self.assertTrue(self.stm.disable_witness())

        # Test enable w/o key
        self.assertTrue(self.stm.update())

        # Test enable w/ key
        self.assertTrue(self.stm.update(wif))

        # Test lock fail
        gp.return_value = secondpass
        self.stm.lock()
        self.assertFalse(self.stm.update())

    def test_keygen(self):
        # Tests keygen function with previously generated brainkey and chosen
        # sequence number
        self.stm.unlock(firstpass)
        bk = self.stm.keygen(brain=brain, seq=5)
        self.assertTrue(bk['brainkey'] == brain)
        self.assertTrue(bk['privkey'].__str__() == privkey)
        self.assertTrue(bk['pubkey'].__str__() == pubkey)

    def test_witlist(self):
        # Barely a test
        self.stm.witlist()

    def test_suggest_bk(self):
        # Test suggest brain key function
        self.stm.unlock(firstpass)
        bk = self.stm.suggest_brain()
        self.assertTrue(len(bk['brainkey']) > 0)
        self.assertTrue(len(bk['privkey'].__str__()) > 0)
        self.assertTrue(len(bk['pubkey'].__str__()) > 0)

    def test_get_missed(self):
        # Test getting missed blocks
        # conf.d test
        m = self.stm.get_missed()
        self.assertTrue(m >= 0)

        # name test
        m = self.stm.get_missed(name=realacc)
        self.assertTrue(m >= 0)

        # fake test
        m = self.stm.get_missed(name=fakename)
        self.assertFalse(m)

    def test_price_feed(self):
        # Test getting price feed
        # conf.d test
        p = self.stm.get_price_feed()
        self.assertTrue(p > 0.001)

        # name test
        p = self.stm.get_price_feed(name=realacc)
        self.assertTrue(p > 0.001)

        # fake test
        self.assertFalse(self.stm.get_price_feed(name=fakename))

    @mock.patch('getpass.getpass')
    def test_change_key(self, gp):
        # Test changing public signing key
        # Lock fail
        self.stm.lock()
        gp.return_value = "blblblb"
        self.assertFalse(self.stm.change_key(pubkey))

        self.stm.unlock(firstpass)
        self.assertFalse(self.stm.change_key(''))
        self.assertTrue(self.stm.change_key(pubkey))

        # Test key change
        self.stm.lock()
        gp.return_value = firstpass
        self.assertTrue(self.stm.change_key(pubkey))

    @mock.patch('getpass.getpass')
    def test_pubfeed(self, gp):
        # Test pubfeed function

        print(self.stm.is_wallet())
        print(self.stm.locked())
        print(self.stm.stm.wallet.masterpassword)
        self.stm.lock()
        print(self.stm.locked())
        print(self.stm.stm.wallet.masterpassword)

        gp.return_value = firstpass
        self.assertTrue(self.stm.pubfeed(0.800))

        self.stm.lock_wallet()
        print(self.stm.locked())
        gp.return_value = secondpass
        print(self.stm.pubfeed(0.800))
        self.assertFalse(self.stm.pubfeed(0.800))

    def test_hard_key(self):
        #test add hard key function and functionality
        self.stm.add_hard_key(True, wif)
        self.assertTrue(self.stm.unlocked())
        self.stm = SteemExplorer(con = self.conf, log = self.log,
                                nobroadcast = True)
        self.stm.delete_wallet()
        self.stm.create_wallet(firstpass)
        self.stm.lock()


    def test_set_props(self):
        self.stm = SteemExplorer(con = self.conf, log = self.log,
                                nobroadcast = True)
        self.assertTrue(self.stm.witness_set_properties(pubkey))
        self.assertTrue(self.stm.witness_set_properties())

"""Placeholder for space."""
