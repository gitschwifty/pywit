from .pywallet import PyWallet
from .config import Configuration
from .interface import SteemExplorer
from .pricefeeds import PriceFeed
from .logger import Logger
from .monitor import WitnessMonitor
import click

conf = Configuration()
log = Logger()
stm = SteemExplorer(con=conf, log=log, nobroadcast=False)

"""Add more options?"""
@click.group(invoke_without_command=True)
@click.option('-v', '--verbose', count=True, help='Verbosity level: default 1, max 3', default=1)
@click.option('-t', '--test', is_flag=True, help='No broadcast mode for testing.')
@click.pass_context
def pywit(ctx, verbose, test):
    log.add_func("Pywit:pywit")
    log.set_level(verbose)
    logstr = "Setting verbosity to {}".format(verbose)
    log.log(logstr, 2)
    if test:
        stm.change_broadcast(True)
        log.log("Activating testing mode.", 1)
    if ctx.invoked_subcommand is None:
        p = PyWallet(stm=stm)
        p.cmdloop()
    else:
        if check_config():
            pass
        else:
            log.log("Configuration or wallet not created. Run 'pywit'. Exiting", 1)
            quit(0)

"""Definitely add more quick commands, status, enable, etc."""

@pywit.command()
@click.option('-w', '--wait', default=6000, help='Seconds to wait between updates.')
@click.option('-s', '--min-spread', default=2.0, help='Minimum price difference (%) to publish new pricefeed.')
@click.option('-n', '--publish-now', is_flag=True, help='Immediately publish a price feed when starting.')
def feeds(wait, min_spread, publish_now):
    p = PriceFeed(stm=stm)
    p.run_feeds(wait, min_spread, publish_now)

@pywit.command()
@click.option('-b', '--backup-key', default='', help='Backup key to switch to.')
@click.option('-m', '--missed-blocks', default=5, help='Missed blocks before disabling/switching.')
@click.option('-w', '--wait', default=300, help='Seconds to wait between checks.')
def monitor(backup_key, missed_blocks, wait):
    m = WitnessMonitor(stm=stm, update_time=wait, missed=missed_blocks, backup=backup_key)
    m.monitor_witness()

@pywit.command()
@click.option('-k', '--key', default='', help='Key to enable.')
def enable(key):
    if key:
        stm.update(key=self.b)
    else:
        stm.update()

@pywit.command()
def disable():
    stm.disable_witness()

@pywit.command()
def status():
    stm.print_witness()

@pywit.command()
def update():
    conf.check_config(self.conf.d['owner'])
    conf.ask_config(self.conf.d['owner'])

    conf.print_json(conf.d)

    ans = click.confirm("Would you like to confirm these updates?", default=True)
    if(ans):
       conf.write_config()
       stm.update(enable=True)
    else:
        conf.check_config(self.conf.d['owner'])
        log.log("Witness updates discarded.", 1)

def check_config():
    if stm.is_wallet() and conf.is_config():
        return True
    return False
