import click
import getpass
import cmd2
from pprint import pprint
from prettytable import PrettyTable
from .config import Configuration
from .interface import SteemExplorer
from .pricefeeds import PriceFeed
from .logger import Logger
from .monitor import WitnessMonitor

"""Maybe remove the logger from this file altogether, only use it for automated
functions. History, etc. will work for the rest of the pywallet commands through
cmd2"""
class PyWallet(cmd2.Cmd):
    """Python Steem Wallet Interface using Beem."""

    def __init__(self, stm: SteemExplorer):
        super().__init__()
        self.register_postcmd_hook(self.unlockedhook)
        self.allow_cli_args = False
        self.hidden_commands.append('edit')
        self.hidden_commands.append('py')
        self.hidden_commands.append('load')
        self.hidden_commands.append('pyscript')
        self.hidden_commands.append('set')
        self.hidden_commands.append('shell')
        self.hidden_commands.append('test')
        self.stm = stm
        self.conf = stm.conf
        self.log = stm.log

    def preloop(self) -> None:
        self.poutput("Python Steem Wallet Interface")
        if not self.conf.is_config():
            self.prompt = ">>> "
            print("Initializing your witness.")
            self.do_init()
        elif not self.stm.is_wallet():
            self.prompt = ">>> "
            print("Initializing your wallet.")
            self.do_new_wallet()
        else:
            self.prompt = "Locked >>> "
        return None

    def postloop(self):
        self.stm.lock_wallet()
        print("Pywit closing now.")

    def unlockedhook(self, data: cmd2.plugin.PostcommandData) -> cmd2.plugin.PostcommandData:
        if self.stm.unlocked():
            self.prompt = ">>> "
        return data

    def do_init(self, name=''):
        """Run: 'init [witness_name]' or 'init'
        Initialize your witness configuration."""
        if self.conf.is_config():
            print("Your witness account %s is already initialized." % self.conf.d['owner'])
        else:
            if name:
                print("Checking your witness information.")
            else:
                name = click.prompt("What is the name of your witness?", type=str)
            if self.conf.check_config(name):
                print("Your witness account was initialized from the network.")
            else:
                self.conf.ask_config(name)
                pprint(conf.d)
                self.conf.write_config()
                print("Your configuration has been initialized.")

        if not self.stm.is_wallet():
            print("Initializing your wallet.")
            self.do_new_wallet()

        #ask them if they want to enable witness

    def do_new_wallet(self, line=''):
        """Usage: 'new_wallet'
        Initialize your wallet configuration."""
        if self.stm.is_wallet():
            print("Your wallet is already initialized.")
        else:
            self.do_create_wallet()
            self.do_unlock()
            if self.stm.unlocked():
                self.do_addkey()
                print("Your wallet is initialized!")
            else:
                print("Failed to unlock wallet.")

    def do_update_witness(self, line=''):
        """Update witness."""
        ans = click.confirm("Would you like to update %s's witness profile?" % self.conf.d['owner'],
                      default=True)
        if ans:
            self.conf.check_config(self.conf.d['owner'])
            self.conf.ask_config(self.conf.d['owner'])

            ## show them all pretty like

            ans = click.confirm("Would you like to confirm these updates?", default=True)
            if(ans):
               self.conf.write_config()
               self.stm.update(enable=True)
            else:
                print("Updates discarded.")
                self.conf.check_config(self.conf.d['owner'])

    def do_addkey(self, key=''):
        """Usage: 'addkey' or 'addkey KEY'
        Add a private key."""
        if key:
            if self.stm.add_key(key):
                print("Your key has been added.")
        else:
            k = click.prompt("Please enter the private key: ", type=str)
            if self.stm.add_key(k):
                print("Your key has been added.")

    def do_unlock(self, line=''):
        """Unlock your wallet."""
        if self.stm.is_wallet():
            if self.stm.unlock_wallet():
                print("Wallet is unlocked.")
                self.prompt = ">>> "
            else:
                print("Unable to unlock wallet.")
        else:
            print("No active wallet.")

    def do_lock(self, line=''):
        """Lock your wallet."""
        if self.stm.is_wallet():
            self.stm.lock_wallet()
        else:
            print("There is no active wallet.")

    def do_create_wallet(self, line=''):
        """Create a new wallet."""
        if self.stm.is_wallet():
            print("A wallet already exists. Please unlock or delete and create a new one.")
        else:
            self.stm.create_wallet()

    def do_delete_wallet(self, line=''):
        """Delete your wallet."""
        ans = click.confirm("Would you really like to delete your wallet?", default=False)
        if ans:
            self.stm.delete_wallet()

    def do_exit(self, line=''):
        """Exit the wallet."""
        return True

    def do_enable(self, pub_key):
        """Usage 'enable PUBLIC_KEY'
        Enable witness."""
        if not pub_key:
            print("Please provide public key.")
            return
        self.conf.check_config(self.conf.d['owner'])
        self.stm.update()
        #call an interface method

    def do_disable(self, line=''):
        """Disable witness."""
        self.conf.check_config(self.conf.d['owner'])
        self.stm.update(enable=False)

    def do_get_witness(self, name=''):
        """Usage: 'get_witness NAME'
        Get witness details."""
        self.stm.print_witness(name)

    def do_status(self, line=''):
        """Your Witness Status."""
        self.conf.check_config(self.conf.d['owner'])
        self.stm.print_witness(self.conf.d['owner'])

    def do_list_witness(self, line=''):
        """Returns data for all witnesses."""
        self.stm.witlist()

    def do_txcost(self, line=''):
        """Calculates cost of a transaction."""
        type = click.prompt("What type of transaction? Comment 1, Vote 2, Transfer 3, Custom Json 4", type=int)
        sz = click.prompt("What size transaction? [Bytes]", type=int)
        if type == 1:
            plen = click.prompt("What is the length of the permlink? [Characters]", type=int)
            pplen = click.prompt("What is the length of the parent permlink? [Characters]", type=int)
        if type == 3:
            plen = click.prompt("How many market operations?", type=int)
        self.stm.compute_cost(type=type, tx_size=sz, perm_len=plen, pperm_len=pplen)

    def do_delete_witness(self, name):
        """Usage: 'delete_witness NAME'
        Deletes witness configuration file."""
        if not name:
            print("Please provide name to delete.")
            return
        self.conf.read_config()
        if self.conf.d['owner'] == name:
            self.conf.delete_config()
            print("%s's witness profile deleted." % name)
        else:
            print("%s's profile is not available." % name)

    def do_add_pubkey(self, key):
        """Usage: 'add_pubkey KEY'
        Adds public signing key to configuration file for monitoring and quick enabling"""
        if not key:
            print("Please provide a key.")
            return
        self.conf.set_pub_key(key)
        if notself.stm.check_key(name=self.conf.d['owner'], key=key):
            ans = click.confirm("Your signing key is not the same as this one. Would you like to enable this key?", default=True)
            if ans:
                 self.do_enable(pub_key=key)

    def do_publish_feed(self, line=''):
        """Publish price feed."""
        pri = click.prompt("Please enter price to publish [SBD/Steem]", type=float)
        self.stm.pubfeed(pri)

    def do_keygen(self, line=''):
        """Generates new private and public key from brainkey.
        Sequence number starts at 0, can regenerate keys by using the same
        sequence number."""
        if self.stm.locked():
            self.do_unlock()
        brain = click.prompt("Enter your brainkey [16 words]", type=str)
        seq = click.prompt("Enter a sequence number", default=0)
        b = self.stm.keygen(brain=brain, seq=seq)
        t = PrettyTable(["Key Type", "Key"])
        t.align = "l"
        t.add_row(["Brain Key: ", b['brainkey']])
        t.add_row(["Private Key [Add to Witness Node]: ", b['privkey']])
        t.add_row(["Public Key [Add to Witness Config]: ", b['pubkey']])
        print(t)
        ans = click.confirm("Add key to wallet?", default=True)
        if ans:
            self.stm.add_key(b['privkey'])

    def do_suggest_brainkey(self, line=''):
        """Suggests a new brain key."""
        if self.stm.locked():
            self.do_unlock()
        b = self.stm.suggest_brain()
        t = PrettyTable(["Key Type", "Key"])
        t.align = "l"
        t.add_row(["Brain Key [Save this]: ", b['brainkey']])
        t.add_row(["Private Key [Add to Witness Node]: ", b['privkey']])
        t.add_row(["Public Key [Add to Witness Config]: ", b['pubkey']])
        print(t)
        ans = click.confirm("Add key to wallet?", default=True)
        if ans:
            self.stm.add_key(b['privkey'])

    def do_print_wallet(self, line=''):
        """Prints out your wallet information (public keys)."""
        if self.stm.locked():
            self.do_unlock()
        t = PrettyTable(["Available Key"])
        t.align = "l"
        for key in self.stm.stm.wallet.getPublicKeys():
            t.add_row([key])
        print(t)

    def do_feeds(self, line=''):
        """Runs a witness price feed."""
        if self.stm.locked():
            self.do_unlock()
        p = PriceFeed(stm=self.stm)
        p.run_feeds()

    def do_monitor(self, line=''):
        """Monitors witness."""
        if self.stm.locked():
            self.do_unlock()
        m = WitnessMonitor(stm=self.stm, update_time=300, missed=5)
        m.monitor_witness()

    def do_check_config(self, line=''):
        """Prints out current configuration file."""
        if self.conf.is_config():
            self.conf.print_json(self.conf.d)
        else:
            print("There is no configuration file available. Please run init.")

    def do_test(self, line=''):
        self.log.add_func("PyWallet:test")
        self.log.set_level(3)
        self.log.log("Testing: Debug verbosity level set to 3.", 3)
        self.log.pop_func()
