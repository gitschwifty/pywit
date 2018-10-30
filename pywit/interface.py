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
from beemgraphenebase.account import BrainKey
from beem.instance import set_shared_steem_instance
from beem.transactionbuilder import TransactionBuilder
from beembase.operations import Comment
from .config import Configuration
from .logger import Logger
from pprint import pprint
from sys import getsizeof
import getpass

DISABLE_KEY = 'STM1111111111111111111111111111111114T1Anm'


class SteemExplorer():
    def __init__(self, con: Configuration, log: Logger, nobroadcast=True):
        self.conf = con
        self.stm = Steem(nobroadcast=nobroadcast)
        self.log = log
        set_shared_steem_instance(self.stm)

    def change_broadcast(self, nobroadcast):
        self.stm = Steem(nobroadcast=nobroadcast)
        set_shared_steem_instance(self.stm)

    def compute_cost(self, type=1, tx_size=1000, perm_len=10, pperm_len=0):
        rc = RC()
        if type == 1:
            cost = rc.comment(
                tx_size=tx_size, permlink_length=perm_len, parent_permlink_length=pperm_len)
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

    def locked(self):
        return not self.stm.wallet.unlocked()

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
            self.log.log("Witness does not exist.", 2)
            return False
        return w.json()

    def print_witness(self, name=''):
        if name:
            try:
                w = Witness(name)
            except WitnessDoesNotExistsException:
                self.log.log("Witness does not exist.", 2)
                return False
            self.conf.print_json(w.json())
        else:
            try:
                w = Witness(self.conf.d['owner'])
            except WitnessDoesNotExistsException:
                self.log.log("Witness does not exist.", 2)
                return False
            self.conf.print_json(w.json())

    def check_key(self, name, key):
        try:
            w = Witness(name)
        except WitnessDoesNotExistsException:
            self.log.log("Witness does not exist.", 2)
            return False
        if key == w['signing_key']:
            return True
        return False

    def disable_witness(self):
        self.update(enable=False)

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
        self.compute_cost(type=1, tx_size=sz, perm_len=len(
            com['permlink']), pperm_len=len(com['parent_permlink']))
        broadcast_tx = tx.broadcast()
        pprint(broadcast_tx)

    def update(self, enable=True, key=''):
        if self.stm.wallet.locked():
            self.unlock_wallet()
        w = Witness(self.conf.d['owner'])
        if enable:
            if key:
                if w.update(key,
                            self.conf.d['url'],
                            self.conf.d['props'],
                            account=self.conf.d['owner']):
                    self.log.log("Witness updated with new parameters.", 2)
            else:
                if w.update(self.conf.d['pub_key'],
                            self.conf.d['url'],
                            self.conf.d['props'],
                            account=self.conf.d['owner']):
                    self.log.log("Witness updated with new parameters.", 2)
        else:
            if w.update(DISABLE_KEY,
                        self.conf.d['url'],
                        self.conf.d['props'], account=self.conf.d['owner']):
                self.log.log("Witness disabled.", 1)

    def change_key(self, pub_key):
        if self.stm.wallet.locked():
            self.unlock_wallet()
        w = Witness(self.conf.d['owner'])
        if w.update(pub_key,
                    self.conf.d['url'],
                    self.conf.d['props'],
                    account=self.conf.d['owner']):
            logstr = "Witness public key updated to {}.".format(pub_key)
            self.log.log(logstr, 1)

    def pubfeed(self, price):
        if self.locked():
            self.unlock_wallet()
        w = Witness(self.conf.d['owner'])
        if w.feed_publish(base=price, quote="1.000 STEEM"):
            logstr = "Feed published: {:.3f} SBD/STEEM".format(price)
            self.log.log(logstr, 1)

    def get_price_feed(self):
        w = Witness(self.conf.d['owner'])
        p = Amount(w.json()['sbd_exchange_rate']['base']).amount
        return p

    def get_missed(self):
        w = Witness(self.conf.d['owner'])
        m = w.json()['total_missed']
        return m

    def keygen(self, brain='', seq=0):
        bk = BrainKey(brainkey=brain, sequence=seq)
        b = dict()
        b['brainkey'] = bk.get_brainkey()
        b['privkey'] = bk.get_private()
        b['pubkey'] = bk.get_public_key()
        return b

    def suggest_brain(self):
        bk = BrainKey()
        b = dict()
        b['brainkey'] = bk.get_brainkey()
        b['privkey'] = bk.get_private()
        b['pubkey'] = bk.get_public_key()
        return b
