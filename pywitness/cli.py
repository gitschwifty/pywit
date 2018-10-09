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
        self.register_preloop_hook(self.prehook)

    def prehook(self) -> None:
        self.poutput("Python Steem Wallet Interface")
        stm.check_wallet()
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
        """Run: 'new_wallet'
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

    def do_update_witness(self, line):
        """Update witness."""
        ans = click.confirm("Would you like to update %s's witness profile?" % conf.d['owner'],
                      default=True)
        if ans:
            conf.check_config(conf.d['owner'])

            key = click.prompt("What is your public signing key?", type=str)

            conf.ask_config(conf.d['owner'])

            ## show them all pretty like

            ans = click.confirm("Would you like to confirm these updates?", default=True)
            if(ans):
                conf.write_config()
                stm.update(pub_key=key)
            else:
                print("Updates discarded.")
                conf.check_config(conf.d['owner'])

    def do_addkey(self, line=''):
        """Add a private key."""
        k = click.prompt("Please enter the private key: ", type=str)
        if stm.add_key(k):
            print("Your key has been added.")

    def do_unlock(self, line=''):
        """Unlock your wallet."""
        if stm.is_wallet():
            p = getpass.getpass("Enter your BIP38 passphrase: ")
            if stm.unlock_wallet(p):
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
            p = getpass.getpass("Please enter your new BIP38 passphrase: ")
            stm.create_wallet(p)

    def do_delete_wallet(self, line=''):
        """Delete your wallet."""
        ans = click.confirm("Would you really like to delete your wallet?", default=False)
        if ans:
            stm.delete_wallet()

    def do_rc(self, name):
        while True:
            stm.get_rc(name)

    def postloop(self):
        print

    def do_test(self, line):
        print("Testing")

    def do_exit(self, line):
        """Exit the wallet."""
        return True

    def do_enable(self, pub_key):
        """Enable witness."""
        conf.check_config(conf.d['owner'])
        stm.update(pub_key)
        #call an interface method

    def do_disable(self, line):
        """Disable witness."""
        conf.check_config(conf.d['owner'])
        stm.update()

    def do_get_witness(self, name):
        """Get witness details."""
        pprint(stm.witness(name))

    def do_status(self, line):
        """Your Witness Status."""
        conf.check_config(conf.d['owner'])
        stm.print_witness(conf.d['owner'])

    def do_feed(self, line):
        """Price Feed."""

    def do_publish_feed(self, line):
        """Publish price feed."""

    def do_keygen(self, line):
        """Generate new key."""

    def do_tickers(self, line):
        """Price tickers."""

    def do_monitor(self, line):
        """Monitor witness."""
        conf = check_conf()
        interface.monitor(conf['owner'])

    def do_list_witness(self, line):
        """Returns data for all witnesses."""
        interface.witlist()

    def do_txcost(self, line):
        """Calculates cost of a transaction."""
        type = click.prompt("What type of transaction? Comment 1, Vote 2, Transfer 3, Custom 4", type=int)
        sz = click.prompt("What size transaction? [Bytes]", type=int)
        plen = click.prompt("What is the length of the permlink? [Characters]", type=int)
        pplen = click.prompt("What is the length of the parent permlink? [Characters]", type=int)
        stm.compute_cost(type=type, tx_size=sz, perm_len=plen, pperm_len=pplen)

    def do_delete_witness(self, name):
        """Deletes witness configuration file."""
        conf.read_config()
        if conf.d['owner'] == name:
            conf.delete_config()
            print("%s's witness profile deleted." % name)
        else:
            print("%s's profile is not available." % name)

def run_loop():
    PyWallet().cmdloop()

if __name__ == '__main__':
    PyWallet().cmdloop()
