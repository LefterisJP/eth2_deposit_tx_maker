# Introduction

If you have tried to use ledger and metamask in eth2 launchpad to create an eth2 deposit transaction it's quite probable that you have come across the `Invalid data received (0x6a80)` error. This is most probably due to this PR not yet merged in metamask: https://github.com/MetaMask/eth-ledger-bridge-keyring/pull/45

This is a tool to help get around this prolem by creating a manual transaction, signing it and then broadcasting it to the network.


# Disclaimer

THIS TOOL IS ONLY GIVEN AS IS AS A WAY TO HELP PEOPLE. DO NOT USE IT IF YOU DO NOT UNDERSTAND WHAT YOU ARE DOING. THE AUTHOR TAKES NO RESPONSIBILITY FOR ANY FUNDS LOST BY USING THE TOOL. 

REALLY DONT USE THIS IF YOU ARE NOT 100% SURE OF WHAT YOU ARE DOING.


# Installation

You need python and node. Ideally this should have been python only but I have not had time to make ledger work with python.

In a python virtual env do:

```
pip install -r requirements.txt
```

And to install the node part:

```
npm install
```

# Usage

## Create unsigned transaction

```
python main.py --deposit-data /path/to/deposit_data.json --eth-rpc-endpoint http://localhost:8545  --gas-price 24.1 --start-nonce 5
```

Replace the deposit data with the location of the json file and the rpc endpoint with your own endpoint. Give an appropriate gas price in gwei and the nonce of the first transaction.

This will create as many transactions as there are deposits with the raw hex of the unsigned transaction being under:

```
--- Deposit N - RLP encoded transaction ---
```


## Get the v, r, s by signing with your ledger

Plug in your ledger and input the pin.

At this point you need to know the derivation index of the ethereum address you want to sign from.

You can see this in ledger live under the details of the account.

It looks like this:

```
44'/60'/1'/0/0
```

The third number is the index. In this case it's 1.

Then to initiate the signing process do:

```npm run start 1 ffffffffffffff```

where 1 is the index of your account and fffffffff is the raw hex of the unsigned transaction.

This should pop up a transaction confirmation screen in your ledger where you should confirm the transaction. Once done three hex should be shown in your screen like this:

```
v: 25
r: fffffffffffffffff
s: eeeeeeeeeeeeee
```

This is what you can use to sign the transaction in the final part.

Repeat the above processes for each transaction

## Sign the transaction

Now take the exact same command you had in the first phase but also add the v, r, s  from the ledger phase as arguments.

```
python main.py --deposit-data /path/to/deposit_data.json --eth-rpc-endpoint http://localhost:8545  --gas-price 24.1 --start-nonce 5 --v 25 --r ffffffffffffffffff --s eeeeeeeeeeeee
```


For multiple tranactions give them comma separated

```
python main.py --deposit-data /path/to/deposit_data.json --eth-rpc-endpoint http://localhost:8545  --gas-price 24.1 --start-nonce 5 --v 25,25 --r ffffffffffffffffff,f1f1f1f1f11f1f1f1f --s eeeeeeeeeeeee,e1e1e1e1e1e1e1e1
```


This will provide each transaction's final signed transaction hex under

`--- Deposit N - signed transaction --- `

## Broadcast the transaction/s

Now take each signed transaction hex from the previous step and broadcast it to the network, either from your own node or from something like mycrypto's push service: https://mycrypto.com/pushTx

