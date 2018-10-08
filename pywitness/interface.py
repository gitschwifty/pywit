import getpass
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
from beem.transactionbuilder import TransactionBuilder
from beembase.operations import Comment
from .config import Configuration
from pprint import pprint
from sys import getsizeof

class SteemExplorer():
    DISABLE_KEY = 'STM1111111111111111111111111111111114T1Anm'

    def __init__(self, con: Configuration, nobroadcast=True, wif=''):
        self.conf = con
        if wif:
            self.stm = Steem(nobroadcast=nobroadcast, keys={'active': wif})
        else:
            self.stm = Steem(nobroadcast=nobroadcast)

    def compute_cost(self, type=1, tx_size=1000, perm_len=10, pperm_len=0):
        rc = RC()
        if type == 1:
            cost = rc.comment(tx_size=tx_size, permlink_length=perm_len, parent_permlink_length=pperm_len)
            print("RC costs for a comment: %.2f G RC" % (cost))
        else:
            print("wtf")

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

    def disable_witness(self, conf: dict):
        print(DISABLE_KEY)

    def witlist(self):
        w = Witnesses()
        w.printAsTable()

    def check_post(self):
        com = dict()
        com = {
            'parent_author': '',
            'parent_permlink': 'chiefs',
            'author': 'petertag',
            'permlink': 'second-update-october-2-jjq9xmvk',
            'title': 'Second Update- October 2',
            'body': 'Not too much to say on the second day of October, especially since my RC is still low due to some live testing I did. I still want to be active, so I\'m just dealing with it.\nSome of these posts in this month of daily posting are going to be missing out on content because it\'s hard to create that much in one space. But that doesn\'t matter, because sports happen weekly!### Chiefs vs. Broncos\nNow I\'m from Kansas City, and live in Denver, so this was quite the game. I also happen to have Patrick Mahomes, Kareem Hunt, and Travis Kelce on my fantasy team, so it was a big game for my fantasy as well (I won, 171.4-134.5 for those keeping score at home). Mahomes missed out on some plays because he was looking out for Von Miller, but Hunt picked up the slack for the Chiefs.\n### That\'s it\nI don\'t actually follow sports too much so that\'s my only opinion on them this week. I\'m working on a python wallet and witness tool for steem, using @Holger80\'s beem python pr',
            'json_metadata': {
                'tags': ('chiefs', 'steem', 'python', 'photography', 'partiko'),
                'image': 'https://s3.us-east-2.amazonaws.com/partiko.io/img/6f5db17aa3252ce18fcce43f0e37677ce21370e3.png',
                'app': 'partiko'
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

    def update(self, pub_key):
        w = Witness(self.conf.d['owner'])
        w['props']['sbd_interest_rate'] = "%s SBD" % w['props']['sbd_interest_rate']
        if pub_key:
            w.update(pub_key, w['url'], w['props'], account=self.conf.d['owner'])
        else:
            w.update(DISABLE_KEY, w['url'], w['props'], account=self.conf.d['owner'])

    def monitor(self, name):
        w = Witness(name)
        w.refresh()
