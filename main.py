import argparse
import json
from pathlib import Path

import rlp
from eth_account._utils.transactions import \
    serializable_unsigned_transaction_from_dict
from web3 import Web3


def get_eth2_deposit_data():
    with Path('data.json').open(mode='r') as f:
        contract_data = json.loads(f.read())
    return contract_data['address'], contract_data['abi']


def make_transactions_for_data(args):
    filepath = Path(args.deposit_data)
    nonce = args.start_nonce
    gas_price = int(args.gas_price * 10 ** 9)
    w3 = Web3(Web3.HTTPProvider(args.eth_rpc_endpoint))
    address, abi = get_eth2_deposit_data()
    deposit_contract = w3.eth.contract(address=address, abi=abi)
    with filepath.open(mode='r') as f:
        deposit_data = json.loads(f.read())

    for entry in deposit_data:
        tx_dict = deposit_contract.functions.deposit(
            entry['pubkey'],
            entry['withdrawal_credentials'],
            entry['signature'],
            entry['deposit_data_root'],
        ).buildTransaction(
            {'gasPrice': gas_price, 'nonce': nonce, 'value': 32000000000000000000},
        )
        unsigned_tx = serializable_unsigned_transaction_from_dict(tx_dict)
        unsigned_tx.hash()  # needed to generate the rlp
        serialized_tx = '0x' + unsigned_tx._cached_rlp.hex()
        print(tx_dict)
        print(serialized_tx)
        nonce += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Uniswap LP tokens address extractor',
        description=(
            'A tool to retrieve all addresses and details of uniswap v2 LP tokens '
            'using multiple data sources. Both an ethereum node and the subgraph'
        ),
    )
    parser.add_argument(
        '--deposit-data',
        help='The filepath to the deposit data json file',
    )
    parser.add_argument(
        '--eth-rpc-endpoint',
        help='The rpc endpoint to an ethereum node',
    )
    parser.add_argument(
        '--start-nonce',
        help='The nonce from which to start the transactions',
        default=0,
        type=int,
    )
    parser.add_argument(
        '--gas-price',
        help='The gas price to set for the transactions in gwei',
        type=int,
    )
    args = parser.parse_args()
    make_transactions_for_data(args)
