# pywit
A Steem wallet and witness tool written in Python using Beempy

Commit at v0.2.0 includes basic witness tools, including updating witness, and several new tools added from v0.1.0. Help in the command line interface will be your friend.
### Do not install if you do not know what you're doing. This software is not fully developed or tested.

Install using `pip3 install -U git+https://github.com/gitschwifty/pywit.git`

This uses beem as a requirement, so the latest version of beempy will be installed with it.
### Uses:

Running `pywit` by itself will get you a command line interface. The first time you open it up, it will run an initialization, getting your witness details and asking if you would like to set up a wallet.

Running `pywit_status` will get the status of your witness.

Running `pywit_enable` will enable your witness with your current signing key, must have set signing key with `add_pubkey` in pywit to use, will be prompted to unlock your wallet.

Running `pywit_disable` will disable your witness, will be prompted to unlock your wallet.
## Commands:
### Interface
`help`<br>
Lists commands, 'help CMD' gives more information on a specific command.

`history`<br>
From cmd2 interface, this shows command history.

`quit`<br>
This quits pywit.

`exit`<br>
Exits pywit.
### Witness
`init`<br>
This is automatically run when you start, initializes your witness.

`update_witness`<br>
This goes through questions to update your witness and send to network.

`enable`<br>
This enables your witness, syntax: `enable SIGNING_KEY`

`disable`<br>
This disables your witness.

`status`<br>
This prints your witness information.

`get_witness`<br>
Gets a witness's details, syntax: `get_witness NAME`    

`list_witness`<br>
This lists the top 100 witnesses as of right now.  
### Wallet
`new_wallet`<br>
This sets up full wallet configuration, run at first run.

`create_wallet`<br>
This creates a wallet for you, just adding the BIP38 passphrase.

`addkey`<br>
This adds a private key to your wallet (wallet must be created and unlocked).

`unlock`<br>
Unlocks your wallet.

`lock`<br>
This locks your wallet.               

`delete_wallet`<br>
This deletes your wallet (WARNING: cannot recover. Make sure you have your keys somewhere else)
### Miscellaneous
`txcost`<br>
This calculates the cost of a transaction, must know byte size of tx for this, doesn't check a full post for you.
### Configuration File
`add_pubkey`<br>
Adds a public key to your configuration file for quick enabling of your witness.
`delete_witness`<br>
Deletes your witness configuration file, syntax: `delete_witness NAME` and name must match configuration file.
#### Currently Unimplemented
`publish_feed`<br>
Unimplemented as of right now, this will allow you to publish a price feed for your witness.

`feed`<br>
Unimplemented, this will automatically run your price feed for you.   

`monitor`<br>
Unimplemented, this will monitor your witness and kill or switch keys if missing blocks  

`keygen`<br>
Unimplemented, this will generate a new key for you.

`tickers`<br>
Unimplemented, this will show you tickers for steem price from several exchanges.       
