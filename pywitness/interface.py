from beem import Steem
from beem.account import Account
from beem.amount import Amount
from beem.rc import RC
from beem.witness import (
    Witness,
    WitnessDoesNotExistsException,
    WitnessesRankedByVote,
    Witnesses,
    WitnessesObject,
)
from beem.wallet import (
    NoWalletException,
)
from beem.instance import set_shared_steem_instance
from beem.transactionbuilder import TransactionBuilder
from beembase.operations import Comment
from .config import Configuration
from pprint import pprint
from sys import getsizeof
import getpass

class SteemExplorer():
    DISABLE_KEY = 'STM1111111111111111111111111111111114T1Anm'

    def __init__(self, con: Configuration, nobroadcast=True):
        self.conf = con
        self.stm = Steem(nobroadcast=nobroadcast)
        set_shared_steem_instance(self.stm)

    def compute_cost(self, type=1, tx_size=1000, perm_len=10, pperm_len=0):
        rc = RC()
        if type == 1:
            cost = rc.comment(tx_size=tx_size, permlink_length=perm_len, parent_permlink_length=pperm_len)
        elif type == 2:
            cost = rc.vote(tx_size=tx_size)
        elif type == 3:
            cost = rc.transfer(tx_size=tx_size, market_op_count=perm_len)
        elif type == 4:
            cost = rc.custom_json(tx_size=tx_size)
        else:
            print("Invalid type.")
            return
        print("RC costs for a comment: %.2f G RC" % (cost))

    def is_wallet(self):
        return self.stm.wallet.created()

    def unlocked(self):
        return self.stm.wallet.unlocked()

    def unlock_wallet(self):
        p = getpass.getpass("Enter your BIP38 passphrase: ")
        if p:
            self.stm.wallet.unlock(p)
            return True
        else:
            print("Need passphrase to unlock wallet.")
            return False

    def lock_wallet(self):
        self.stm.wallet.lock()

    def check_wallet(self):
        if self.stm.wallet.MasterPassword.config_key:
            print("Master password exists.")

    def create_wallet(self):
        p = getpass.getpass("Enter your new BIP38 passphrase: ")
        if p:
            self.stm.wallet.create(p)
            return True
        else:
            print("Please enter a passphrase to create wallet.")
            return False

    def add_key(self, key):
        if key:
            if self.is_wallet():
                if self.unlocked():
                    self.stm.wallet.addPrivateKey(key)
                    return True
                else:
                    print("Please unlock wallet.")
                    return False
            else:
                print("There is no active wallet.")
                return False
        else:
            print("Please enter a key.")
            return False

    def delete_wallet(self):
        self.stm.wallet.wipe(True)

    def get_rc(self, account_name):
        acc = Account(account_name)
        mana = acc.get_rc_manabar()
        print("Current Mana: %i" % mana['current_mana'])
        print("Percentage: %f" % mana['current_pct'])

    def witness_json(self, name):
        try:
            w = Witness(name)
        except WitnessDoesNotExistsException:
            return False
        return w.json()

    def print_witness(self, name):
        try:
            w = Witness(name)
        except WitnessDoesNotExistsException:
            return False
        self.conf.print_json(w.json())

    def check_key(self, name, key):
        try:
            w = Witness(name)
        except WitnessDoesNotExistsException:
            return False
        if key == w['signing_key']:
            return True
        return False

    def disable_witness(self):
        self.update()

    def witlist(self):
        w = Witnesses()
        w.printAsTable()

    def check_post(self):
        com = dict()
        com = {
            'parent_author': '',
            'parent_permlink': 'steem',
            'author': 'me',
            'permlink': 'testpost',
            'title': 'testpost pls ignore',
            'body': 'do not upvote',
            'json_metadata': {
                'tags': ('test', 'post', 'pls', 'ignore', 'steem'),
            }
        }
        print(len(com['body']))
        tx = TransactionBuilder(steem_instance=self.stm)
        tx.appendOps(Comment(com))
        tx.appendSigner("petertag", "active")
        signed_tx = tx.sign()
        sz = getsizeof(com)
        pprint(com)
        pprint(signed_tx)
        print("Size is %i" % sz)
        self.compute_cost(type=1, tx_size=sz, perm_len=len(com['permlink']), pperm_len=len(com['parent_permlink']))
        broadcast_tx = tx.broadcast()
        pprint(broadcast_tx)

    def update(self, enable=True):
        if self.stm.wallet.locked():
            self.unlock_wallet()
        w = Witness(self.conf.d['owner'])
        w['props']['sbd_interest_rate'] = "%s SBD" % w['props']['sbd_interest_rate']
        if enable:
            w.update(self.conf.d['pub_key'], self.conf.d['url'], self.conf.d['props'], account=self.conf.d['owner'])
        else:
            w.update(DISABLE_KEY, self.conf.d['url'], self.conf.d['props'], account=self.conf.d['owner'])

    def monitor(self, name):
        w = Witness(name)
        w.refresh()
