import click
import getpass
from .config import Configuration
from .interface import SteemExplorer
from pprint import pprint
from cmd2 import Cmd

conf = Configuration()
stm = SteemExplorer(con=conf)

class PyWallet(Cmd):
    """Python Steem Wallet Interface using Beem."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def preloop(self) -> None:
        self.poutput("Python Steem Wallet Interface")
        if not conf.is_config():
            self.prompt = ">>> "
            print("Initializing your witness.")
            self.do_init()
        elif not stm.is_wallet():
            self.prompt = ">>> "
            print("Initializing your wallet.")
            self.do_new_wallet()
        else:
            self.prompt = "Locked >>> "
        return None

    def postloop(self):
        stm.lock_wallet()
        print("Pywit closing now.")

    def do_init(self, name=''):
        """Run: 'init [witness_name]' or 'init'
        Initialize your witness configuration."""
        if conf.is_config():
            print("Your witness account %s is already initialized." % conf.d['owner'])
        else:
            if name:
                print("Checking your witness information.")
            else:
                name = click.prompt("What is the name of your witness?", type=str)
            if conf.check_config(name):
                print("Your witness account was initialized from the network.")
            else:
                conf.ask_config(name)
                pprint(conf.d)
                conf.write_config()
                print("Your configuration has been initialized.")

        if not stm.is_wallet():
            print("Initializing your wallet.")
            self.do_new_wallet()

        #ask them if they want to enable witness

    def do_new_wallet(self, line=''):
        """Usage: 'new_wallet'
        Initialize your wallet configuration."""
        if stm.is_wallet():
            print("Your wallet is already initialized.")
        else:
            self.do_create_wallet()
            self.do_unlock()
            if stm.unlocked():
                self.do_addkey()
                print("Your wallet is initialized!")
            else:
                print("Failed to unlock wallet.")

    def do_update_witness(self, line=''):
        """Update witness."""
        ans = click.confirm("Would you like to update %s's witness profile?" % conf.d['owner'],
                      default=True)
        if ans:
            conf.check_config(conf.d['owner'])
            conf.ask_config(conf.d['owner'])

            ## show them all pretty like

            ans = click.confirm("Would you like to confirm these updates?", default=True)
            if(ans):
                conf.write_config()
                stm.update(enable=True)
            else:
                print("Updates discarded.")
                conf.check_config(conf.d['owner'])

    def do_addkey(self, key=''):
        """Usage: 'addkey' or 'addkey KEY'
        Add a private key."""
        if k:
            if stm.add_key(k):
                print("Your key has been added.")
        else:
            k = click.prompt("Please enter the private key: ", type=str)
            if stm.add_key(k):
                print("Your key has been added.")

    def do_unlock(self, line=''):
        """Unlock your wallet."""
        if stm.is_wallet():
            if stm.unlock_wallet():
                print("Wallet is unlocked.")
                self.prompt = ">>> "
            else:
                print("Unable to unlock wallet.")
        else:
            print("No active wallet.")

    def do_lock(self, line=''):
        """Lock your wallet."""
        if stm.is_wallet():
            stm.lock_wallet()
        else:
            print("There is no active wallet.")

    def do_create_wallet(self, line=''):
        """Create a new wallet."""
        if stm.is_wallet():
            print("A wallet already exists. Please unlock or delete and create a new one.")
        else:
            stm.create_wallet()

    def do_delete_wallet(self, line=''):
        """Delete your wallet."""
        ans = click.confirm("Would you really like to delete your wallet?", default=False)
        if ans:
            stm.delete_wallet()

    def do_test(self, line=''):
        print("Testing")

    def do_exit(self, line=''):
        """Exit the wallet."""
        return True

    def do_enable(self, pub_key):
        """Usage 'enable PUBLIC_KEY'
        Enable witness."""
        if not pub_key:
            print("Please provide public key.")
            return
        conf.check_config(conf.d['owner'])
        stm.update()
        #call an interface method

    def do_disable(self, line=''):
        """Disable witness."""
        conf.check_config(conf.d['owner'])
        stm.update(enable=False)

    def do_get_witness(self, name=''):
        """Usage: 'get_witness NAME'
        Get witness details."""
        pprint(stm.witness(name))

    def do_status(self, line=''):
        """Your Witness Status."""
        conf.check_config(conf.d['owner'])
        stm.print_witness(conf.d['owner'])

    def do_list_witness(self, line=''):
        """Returns data for all witnesses."""
        interface.witlist()

    def do_txcost(self, line=''):
        """Calculates cost of a transaction."""
        type = click.prompt("What type of transaction? Comment 1, Vote 2, Transfer 3, Custom Json 4", type=int)
        sz = click.prompt("What size transaction? [Bytes]", type=int)
        if type == 1:
            plen = click.prompt("What is the length of the permlink? [Characters]", type=int)
            pplen = click.prompt("What is the length of the parent permlink? [Characters]", type=int)
        if type == 3:
            plen = click.prompt("How many market operations?", type=int)
        stm.compute_cost(type=type, tx_size=sz, perm_len=plen, pperm_len=pplen)

    def do_delete_witness(self, name):
        """Usage: 'delete_witness NAME'
        Deletes witness configuration file."""
        if not name:
            print("Please provide name to delete.")
            return
        conf.read_config()
        if conf.d['owner'] == name:
            conf.delete_config()
            print("%s's witness profile deleted." % name)
        else:
            print("%s's profile is not available." % name)

    def do_add_pubkey(self, key):
        """Usage: 'add_pubkey KEY'
        Adds public signing key to configuration file for monitoring and quick enabling"""
        if not key:
            print("Please provide a key.")
            return
        conf.set_pub_key(key)
        if not stm.check_key(name=conf.d['owner'], key=key):
            ans = click.confirm("Your signing key is not the same as this one. Would you like to enable this key?", default=True)
            if ans:
                self.do_enable(pub_key=key)

    def do_feed(self, line=''):
        """Uninimplemented Price Feed."""

    def do_publish_feed(self, line=''):
        """Uninimplemented Publish price feed."""

    def do_keygen(self, line=''):
        """Uninimplemented Generate new key."""

    def do_tickers(self, line=''):
        """Uninimplemented Price tickers."""

    def do_monitor(self, line=''):
        """Uninimplemented Monitor witness."""

def enable():
    p = PyWallet()
    if conf.d['pub_key']:
        p.do_enable(pub_key=conf.d['pub_key'])
    else:
        print("Must have a set public key to enable. Run 'add_pubkey KEY' in Pywit.")

def status():
    p = PyWallet()
    p.do_status()

def disable():
    p = PyWallet()
    p.do_disable()

def run_loop():
    p = PyWallet()
    p.cmdloop()
