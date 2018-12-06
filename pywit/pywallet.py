import click
import cmd2

from prettytable import PrettyTable
from .util import print_json
from .config import Configuration
from .interface import SteemExplorer
from .pricefeeds import PriceFeed
from .monitor import WitnessMonitor


class PyWallet(cmd2.Cmd):
    """Python Steem Wallet Interface using Beem."""

    def __init__(self, stm):
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

    def preloop(self) -> None:
        self.poutput("Python Steem Wallet Interface")
        if not self.conf.is_config():
            self.prompt = ">>> "
            self.poutput("Initializing your witness.")
            self.do_init()
        elif not self.stm.is_wallet():
            self.prompt = ">>> "
            self.poutput("Initializing your wallet.")
            self.do_new_wallet()
        else:
            self.prompt = "Locked >>> "
        return None

    def postloop(self):
        self.stm.lock_wallet()
        self.poutput("Pywit closing now.")

    def unlockedhook(self,
                     data: cmd2.plugin.PostcommandData) -> cmd2.plugin.PostcommandData:
        if self.stm.unlocked():
            self.prompt = ">>> "
        return data

    def do_init(self, name=''):
        """Run: 'init [witness_name]' or 'init'
        Initialize your witness configuration."""
        if self.conf.is_config():
            self.poutput("Your witness account %s is already initialized." %
                         self.conf.d['owner'])
        else:
            if name:
                self.poutput("Checking your witness information.")
            else:
                name = click.prompt(
                    "What is the name of your witness?", type=str)
            if self.conf.check_config(name):
                self.poutput(
                    "Your witness account was initialized from the network.")
            else:
                self.conf.ask_config(name)
                self.poutput(self.conf.d)
                self.conf.write_config()
                self.poutput("Your configuration has been initialized.")

        if not self.stm.is_wallet():
            self.poutput("Initializing your wallet.")
            self.do_new_wallet()

        # ask them if they want to enable witness

    def do_new_wallet(self, line=''):
        """Usage: 'new_wallet'
        Initialize your wallet configuration."""
        if self.stm.is_wallet():
            self.poutput("Your wallet is already initialized.")
        else:
            self.do_create_wallet()
            self.prompt = ">>> "
            self.do_addkey()
            self.poutput("Your wallet is initialized!")

    def do_update_witness(self, line=''):
        """Update witness."""
        ans = click.confirm("Would you like to update %s's witness profile?" % self.conf.d['owner'],
                            default=True)
        if ans:
            self.conf.check_config(self.conf.d['owner'])
            self.conf.ask_config(self.conf.d['owner'])

            # show them all pretty like

            ans = click.confirm(
                "Would you like to confirm these updates?", default=True)
            if(ans):
                self.conf.write_config()
                self.stm.witness_set_properties()
            else:
                self.poutput("Updates discarded.")
                self.conf.check_config(self.conf.d['owner'])

    def do_addkey(self, key=''):
        """Usage: 'addkey' or 'addkey KEY'
        Add a private key."""
        if not key:
            key = click.prompt("Please enter your private key", type=str)
        if self.stm.add_key(key):
            self.poutput("Your key has been added.")
        else:
            self.poutput("Unable to add key to wallet.")

    def do_unlock(self, line=''):
        """Unlock your wallet."""
        if self.stm.is_wallet():
            if self.stm.unlock_wallet():
                self.poutput("Wallet is unlocked.")
                self.prompt = ">>> "
            else:
                self.poutput("Unable to unlock wallet.")
        else:
            self.poutput("No active wallet.")

    def do_lock(self, line=''):
        """Lock your wallet."""
        if self.stm.is_wallet():
            self.stm.lock_wallet()
        else:
            self.poutput("There is no active wallet.")

    def do_create_wallet(self, line=''):
        """Create a new wallet."""
        if self.stm.is_wallet():
            self.poutput("A wallet already exists. Please unlock or delete and \
                create a new one.")
        else:
            if not self.stm.create_wallet():
                self.poutput("Unable to create wallet.")

    def do_delete_wallet(self, line=''):
        """Delete your wallet."""
        ans = click.confirm(
            "Would you really like to delete your wallet?", default=False)
        if ans:
            self.stm.delete_wallet()

    def do_exit(self, line=''):
        """Exit the wallet."""
        return True

    def do_enable(self, pub_key):
        """Usage 'enable PUBLIC_KEY'
        Enable witness."""
        if not pub_key:
            self.poutput("Please provide public key.")
            return
        self.conf.check_config(self.conf.d['owner'])
        self.stm.update()
        # call an interface method

    def do_disable(self, line=''):
        """Disable witness."""
        self.conf.check_config(self.conf.d['owner'])
        self.stm.update(enable=False)

    def do_get_witness(self, name):
        """Usage: 'get_witness NAME'
        Get witness details."""
        w = self.stm.witness_json(name)
        if w:
            print_json(w)

    def do_status(self, line=''):
        """Your Witness Status."""
        self.conf.check_config(self.conf.d['owner'])
        print_json(self.stm.witness_json(self.conf.d['owner']))

    def do_list_witness(self, line=''):
        """Returns data for all witnesses."""
        self.stm.witlist()

    def do_txcost(self, line=''):
        """Calculates cost of a transaction."""
        t = click.prompt(
            "What type of transaction? Comment 1, Vote 2, Transfer 3, Custom Json 4",
            type=int)
        sz = click.prompt("What size transaction? [Bytes]", type=int)
        if t == 1:
            plen = click.prompt(
                "What is the length of the permlink? [Characters]",
                type=int)
            pplen = click.prompt(
                "What is the length of the parent permlink? [Characters]",
                type=int)
            c = self.stm.compute_cost(type=t, tx_size=sz,
                                      perm_len=plen, pperm_len=pplen)
        elif t == 3:
            plen = click.prompt("How many market operations?", type=int)
            c = self.stm.compute_cost(type=t, tx_size=sz,
                                      perm_len=plen)
        else:
            c = self.stm.compute_cost(type=t, tx_size=sz)
        self.poutput("Transaction cost: %i RC." % c)

    def do_delete_witness(self, name):
        """Usage: 'delete_witness NAME'
        Deletes witness configuration file."""
        if not name:
            self.poutput("Please provide name to delete.")
            return
        self.conf.read_config()
        if self.conf.d['owner'] == name:
            self.conf.delete_config()
            self.poutput("%s's witness profile deleted." % name)
        else:
            self.poutput("%s's profile is not available." % name)

    def do_add_pubkey(self, key):
        """Usage: 'add_pubkey KEY'
        Adds public signing key to configuration file for monitoring and quick enabling"""
        if not key:
            self.poutput("Please provide a key.")
            return
        self.conf.set_pub_key(key)
        if not self.stm.check_key(name=self.conf.d['owner'], key=key):
            ans = click.confirm(
                "Your signing key is not the same as this one. Would you like to enable this key?",
                default=True)
            if ans:
                self.do_enable(pub_key=key)

    def do_publish_feed(self, line=''):
        """Publish price feed."""
        pri = click.prompt(
            "Please enter price to publish [SBD/Steem]", type=float)
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
        self.poutput(t)
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
        self.poutput(t)
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
        self.poutput(t)

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
            print_json(self.conf.d)
        else:
            self.poutput(
                "There is no configuration file available. Please run init.")

    def do_change_passphrase(self, line=''):
        """Changes your wallet's BIP38 passphrase."""
        if self.stm.change_passphrase():
            self.poutput("Your passphrase has been changed.")
        else:
            self.poutput("Unable to change your passphrase.")

    def do_get_rc(self, user=''):
        """Check your or another user's resource credits."""
        if user:
            m = self.stm.get_rc(user)
        else:
            m = self.stm.get_rc(self.conf.d['owner'])
        print("Current RC: %i" % m['current_mana'])
        print("Percentage: %f" % m['current_pct'])

    def do_test(self, line=''):
        """Testing..."""
        self.poutput("Do your tests.")
