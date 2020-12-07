import argparse
import json
from pathlib import Path

from eth_account._utils.transactions import (
    encode_transaction,
    serializable_unsigned_transaction_from_dict,
)
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

    v_vals = r_vals = s_vals = None
    if args.v is not None:
        v_vals = [int(x, 16) for x in args.v.split(',')]
        r_vals = [int(x, 16) for x in args.r.split(',')]
        s_vals = [int(x, 16) for x in args.s.split(',')]
        assert len(v_vals) == len(r_vals) == len(s_vals)

    transactions = []
    for idx, entry in enumerate(deposit_data):
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
        transactions.append(serialized_tx)
        print(f' --- Deposit {idx} - Transaction object --- ')
        print(tx_dict)
        print(f' --- Deposit {idx} - RLP encoded transaction --- ')
        print(serialized_tx)
        if v_vals and len(v_vals) >= idx + 1:
            signed_tx = encode_transaction(unsigned_tx, (v_vals[idx], r_vals[idx], s_vals[idx]))
            print(f' --- Deposit {idx} - signed transaction --- ')
            print('0x' + signed_tx.hex())
        print('\n')
        nonce += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Eth2 deposit tx maker',
        description='Tool to generate unsigned transactions for eth2 deposits',
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
        type=float,
    )
    parser.add_argument(
        '--v',
        default=None,
        type=str,
    )
    parser.add_argument(
        '--r',
        default=None,
        type=str,
    )
    parser.add_argument(
        '--s',
        default=None,
        type=str,
    )
    args = parser.parse_args()
    make_transactions_for_data(args)
