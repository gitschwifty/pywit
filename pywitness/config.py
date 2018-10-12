import json
import os
import click
from os.path import expanduser, isfile
from beem.amount import Amount
from beem.witness import (
    Witness,
    WitnessDoesNotExistsException,)

class Configuration():

    d = dict()

    def __init__(self, file='~/.pywitness.json'):
        self.file = os.path.expanduser(file)
        if self.is_config():
            self.read_config()
        else:
            self.d = {
                'owner': '',
                'url': 'https://www.steemd.com/witnesses',
                'pub_key': '',
                'props': {  'account_creation_fee': {'amount': '3000',
                                                     'nai': '@@000000021',
                                                     'precision': 3},
                            'account_subsidy_budget': 797,
                            'account_subsidy_decay': 347321,
                            'maximum_block_size': 65536,
                            'sbd_interest_rate': 0,
                        }}

    def read_config(self):
        with open(self.file, 'r') as f:
            self.d = json.loads(f.read())

    def write_config(self):
        with open(self.file, 'w') as f:
            f.write(json.dumps(self.d, indent=4))

    def print_json(self, js):
        print(json.dumps(js, indent=4))

    def is_config(self):
        return os.path.isfile(self.file)

    def delete_config(self):
        os.remove(self.file)

    def check_config(self, name):
        self.d['owner'] = name
        try:
            w = Witness(name)
        except WitnessDoesNotExistsException:
            return False
        wj = w.json()
        self.d['props'] = wj['props']
        self.d['url'] = wj['url']
        self.write_config()
        return True

    def ask_config(self, name):
        self.d['url'] = click.prompt("What is your witness URL?", type=str, default=self.d['url'])
        default_fee = self.get_float_amount(self.d['props']['account_creation_fee'])
        creation_fee = click.prompt(
                        "What should the account creation fee be (STEEM)?",
                        default=default_fee)
        while True:
            try:
                creation_fee = "%s STEEM" % float(creation_fee)
                break
            except ValueError:
                creation_fee = click.prompt(
                                "Please enter a numerical value (STEEM)?",
                                default=default_fee)

        self.d['props']['account_creation_fee'] = self.get_amount_json(creation_fee)

        self.d['props']['account_subsidy_budget'] = click.prompt(
                                "What should the account subsidy budget be?",
                                default=self.d['props']['account_subsidy_budget'])

        self.d['props']['account_subsidy_decay'] = click.prompt(
                                "What should the account subsidy decay rate be?",
                                default=self.d['props']['account_subsidy_decay'])

        self.d['props']['sbd_interest_rate'] = click.prompt(
                                "What should the SBD interest rate be?",
                                default=self.d['props']['sbd_interest_rate'])

        self.d['pub_key'] = click.prompt("What is your public signing key?",
                                type=str,
                                default=self.d['pub_key'])

        #maximum_block_size not included because you shouldn't change that

    def set_pub_key(self, key):
        self.d['pub_key'] = key
        self.write_config()

    def get_amount_json(self, str):
        return Amount(str).json()

    def get_float_amount(self, amt: dict):
        return Amount(amt).amount
