import click
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
        if not conf.is_config():
            self.prompt = ">>> "
            self.do_init()
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

                #ask them if they want to enable witness
                #ask if they want to add a wallet

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
