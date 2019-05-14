import getpass

from beem import Steem
from beem.account import Account
from beem.rc import RC
from beem.witness import (
    Witness,
    WitnessDoesNotExistsException,
    WitnessesRankedByVote,
    Witnesses,
    WitnessesObject,
)
from beem.exceptions import (
    WrongMasterPasswordException,
)
from beemgraphenebase.account import BrainKey
from beem.instance import set_shared_steem_instance

from .config import Configuration
from .logger import Logger

DISABLE_KEY = 'STM1111111111111111111111111111111114T1Anm'
NODE_LIST = ["https://appbasetest.timcliff.com", "https://steemd.minnowsupportproject.org", "https://steemd.privex.org"]

class SteemExplorer():
    def __init__(self, con: Configuration, log: Logger, nobroadcast=True, active=''):
        self.conf = con
        self.stm = Steem(node="https://appbasetest.timcliff.com", nobroadcast=nobroadcast, unsigned=nobroadcast)
        self.stm.set_default_nodes(NODE_LIST)
        self.log = log
        set_shared_steem_instance(self.stm)

    def change_broadcast(self, nobroadcast):
        self.stm = Steem(nobroadcast=nobroadcast, unsigned=nobroadcast)
        set_shared_steem_instance(self.stm)

    def add_hard_key(self, nobroadcast, key):
        self.stm = Steem(nobroadcast=nobroadcast, unsigned=nobroadcast,
                         keys={"active": key})
        set_shared_steem_instance(self.stm)

    def compute_cost(self, type=1, tx_size=1000, perm_len=10, pperm_len=0):
        rc = RC()
        if type == 1:
            cost = rc.comment(tx_size=tx_size, permlink_length=perm_len,
                              parent_permlink_length=pperm_len)
        elif type == 2:
            cost = rc.vote(tx_size=tx_size)
        elif type == 3:
            cost = rc.transfer(tx_size=tx_size, market_op_count=perm_len)
        elif type == 4:
            cost = rc.custom_json(tx_size=tx_size)
        else:
            return False
        return cost

    def is_wallet(self):
        return self.stm.wallet.created()

    def unlocked(self):
        return self.stm.wallet.unlocked()

    def locked(self):
        return not self.unlocked()

    def unlock_wallet(self, p=''):
        if not p:
            p = getpass.getpass("Enter your BIP38 passphrase: ")
        try:
            self.stm.unlock(p)
        except WrongMasterPasswordException:
            return False
        return True

    def lock_wallet(self):
        self.stm.wallet.lock()

    def unlock(self, p=''):
        return self.unlock_wallet(p)

    def lock(self):
        self.stm.wallet.lock()

    def create_wallet(self, p=''):
        if not p:
            p = getpass.getpass("Enter your new BIP38 passphrase: ")
        if p:
            self.stm.wallet.create(p)
            return True
        else:  # pragma: no cover
            return False

    def change_passphrase(self, p=''):
        if not self.__wallet_hook():
            return False
        if not p:
            p = getpass.getpass("Enter your new BIP38 passphrase: ")
        self.stm.wallet.changePassphrase(p)
        return True

    def add_key(self, key):
        if key:
            if not self.__wallet_hook():
                return False
            self.stm.wallet.addPrivateKey(key)
            return True
        else:
            return False

    def delete_wallet(self):
        self.stm.wallet.wipe(True)

    def get_rc(self, account_name):
        acc = Account(account_name)
        mana = acc.get_rc_manabar()
        return mana

    def witness_json(self, name):
        try:
            w = Witness(name)
        except WitnessDoesNotExistsException:
            self.log.log("Witness does not exist.", 2)
            return False
        return w.json()

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
        return self.witness_set_properties(DISABLE_KEY)

    def witlist(self):
        w = Witnesses()
        w.printAsTable()

    def update(self, enable=True, key=''):
        if not self.__wallet_hook():
            return False
        w = Witness(self.conf.d['owner'])
        if enable:
            if key:
                if w.update(key,
                            self.conf.d['url'],
                            self.conf.d['props'],
                            account=self.conf.d['owner']):  # pragma: no cover
                    self.log.log("Witness updated with new parameters.", 2)
                    return True
            else:
                if w.update(self.conf.d['pub_key'],
                            self.conf.d['url'],
                            self.conf.d['props'],
                            account=self.conf.d['owner']):  # pragma: no cover
                    self.log.log("Witness updated with new parameters.", 2)
                    return True
        else:
            if w.update(DISABLE_KEY,
                        self.conf.d['url'],
                        self.conf.d['props'],
                        account=self.conf.d['owner']):  # pragma: no cover
                self.log.log("Witness disabled.", 1)
                return True

    def change_key(self, pub_key):
        if not self.__wallet_hook():
            return False
        w = Witness(self.conf.d['owner'])
        if pub_key:
            if w.update(pub_key,
                        self.conf.d['url'],
                        self.conf.d['props'],
                        account=self.conf.d['owner']):
                logstr = "Witness public key updated to {}.".format(pub_key)
                self.log.log(logstr, 1)
                return True
        else:
            return False

    def pubfeed(self, price):
        if not self.__wallet_hook():
            return False
        w = Witness(self.conf.d['owner'])
        if w.feed_publish(base=price, quote="1.000 STEEM"):
            logstr = "Feed published: {:.3f} SBD/STEEM".format(price)
            self.log.log(logstr, 1)
            return True

    def get_price_feed(self, name=''):
        try:
            if name:
                wjson = Witness(name).json()
                p = (float(wjson['sbd_exchange_rate']['base']['amount'])
                          / 10**wjson['sbd_exchange_rate']['base']['precision'])
            else:
                wjson = Witness(self.conf.d['owner']).json()
                p = (float(wjson['sbd_exchange_rate']['base']['amount'])
                          / 10**wjson['sbd_exchange_rate']['base']['precision'])
        except WitnessDoesNotExistsException:
            return False
        return p

    def get_missed(self, name=''):
        try:
            if name:
                w = Witness(name)
                m = w.json()['total_missed']
            else:
                w = Witness(self.conf.d['owner'])
                m = w.json()['total_missed']
        except WitnessDoesNotExistsException:
            return False
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

    def witness_set_properties(self, pubkey=''):
        if pubkey:
            if self.stm.witness_update(pubkey, self.conf.d['url'],
                                       self.conf.d['props'],
                                       account=self.conf.d['owner']):
                return True
        else:
            if self.stm.witness_update(self.conf.d['pub_key'],
                                       self.conf.d['url'],
                                       self.conf.d['props'],
                                       account=self.conf.d['owner']):
                return True

    def __wallet_hook(self):
        if not self.is_wallet():
            return False

        if self.locked():
            if not self.unlock_wallet():
                return False
        return True
