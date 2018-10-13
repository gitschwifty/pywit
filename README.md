# pywit
A Steem wallet and witness tool written in Python using Beempy

Commit at v0.2.0 includes basic witness tools, including updating witness, and several new tools added from v0.1.0. Help in the command line interface will be your friend.

### Do not install if you do not know what you're doing. This software is not fully developed or tested.

Install using `pip3 install -U git+https://github.com/gitschwifty/pywit.git`

This uses beem as a requirement, so the latest version of beempy will be installed with it.

Uses:

Running 'pywit' by itself will get you a command line interface. The first time you open it up, it will run initialization, getting your witness details and asking if you would like to set up a wallet. These will just be questions asked in the command line.

Running 'pywit_status' will get the status of your witness (if you've set up configuration file).

Running 'pywit_enable' will enable your witness with your current signing key, must have set signing key and wallet in pywit to use, will be prompted to unlock your wallet.

Running 'pywit_disable' will disable your witness, must have set wallet up in pywit to use, will be prompted to unlock your wallet.

Commands:

add_pubkey:
Adds a public key to your configuration file for quick enabling of your witness.

edit:
From cmd2 interface, lets you edit a file in text interface (untested, might remove)

init:
This is done at the first run, initializes your witness.

publish_feed:
Unimplemented as of right now, this will allow you to publish a price feed for your witness.  

status:
This returns a json dict of your witness information.

addkey:
This adds a private key to your wallet (wallet must be created and unlocked)          

enable:
This enables your witness. Must run 'enable SIGNING_KEY'      

keygen:
Unimplemented, this will generate a new key for you.     

py:
From cmd2 interface, this runs python files (untested, might remove)        

tickers:
Unimplemented, this will show you tickers for steem price from several exchanges.

alias:
From cmd2 interface, this aliases a command for you (untested, might remove)         

exit:
Exits pywit.      

list_witness:
This lists the top 100 witnesses as of right now.  

pyscript:
From cmd2 interface, this runs python scripts (untested, might remove)      

txcost:
This calculates the cost of a transaction, must know byte size of tx for this, doesn't check a full post for you.

create_wallet:
This creates a wallet for you, just adding the BIP38 passphrase.

feed:
Unimplemented, this will automatically run your price feed for you.         

load:
From cmd2 interface, this loads a script file (untested, might remove)

quit:
This also quits pywit.        

unalias:
From cmd2 interface, this unaliases a command for you (untested, might remove)

delete_wallet:
This deletes your wallet (WARNING: cannot recover. Make sure you have your keys somewhere else)   

get_witness:
Gets a witness's details, must run 'get_witness NAME'   

lock:
This locks your wallet.        

set:
From cmd2 interface, unsure of use, untested will remove         

unlock:
Unlocks your wallet   

delete_witness:
Deletes your witness configuration file, must run 'delete_witness NAME' and must match configuration file.  

help:
Lists commands, 'help CMD' gives more information on a specific command.         

monitor:
Unimplemented, this will monitor your witness and kill or switch keys if missing blocks      

shell:
From cmd2 interface, this runs a shell, untested will remove.         

update_witness:
This goes through questions to update your witness and send to network.

disable:
This disables your witness.         

history:
From cmd2 interface, this shows command history. Will leave in.      

new_wallet:
This sets up full wallet configuration, run at first run.    

shortcuts:
From cmd2 interface, shows shortcuts, untested might remove.  
