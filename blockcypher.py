from blockexplorer.settings import BLOCKCYPHER_API_KEY

from bitcoins.utils import is_valid_btc_address, is_valid_tx_hash

from dateutil import parser

import requests
import json


COIN_SYMBOL_MAPPINGS = {
        # format like such
        # 'coin_symbol': ('Display Name', 'Blockcypher Code', 'Blockcypher Network', 'Currency Name/Abbrev'),
        'btc': ('Bitcoin', 'btc', 'main', 'BTC'),
        'btc-testnet': ('Bitcoin Testnet', 'btc', 'test3', 'BTC'),
        'ltc': ('Litecoin', 'ltc', 'main', 'LTC'),
        'ltc-testnet': ('Litecoin Testnet', 'ltc', 'test', 'LTC'),
        'uro': ('Uro', 'uro', 'main', 'URO'),
        'bcy': ('BlockCypher Testnet', 'bcy', 'test', 'BCY'),
        }

# WET, but maintains order
COIN_SYMBOL_ORDER_LIST = ('btc', 'btc-testnet', 'ltc', 'ltc-testnet', 'uro', 'bcy')

# Django-Style List
COIN_CHOICES = []
for coin_symbol in COIN_SYMBOL_ORDER_LIST:
    COIN_CHOICES.append((coin_symbol, COIN_SYMBOL_MAPPINGS[coin_symbol][0]))


def get_address_details(address, coin_symbol='btc', max_txns=None):

    # This check appears to work for other blockchains
    # TODO: verify and/or improve
    assert is_valid_btc_address(address)

    url_to_hit = 'https://api.blockcypher.com/v1/%s/%s/addrs/%s' % (
            COIN_SYMBOL_MAPPINGS[coin_symbol][1],
            COIN_SYMBOL_MAPPINGS[coin_symbol][2],
            address)

    # print(url_to_hit)

    params = {}
    if max_txns:
        params['limit'] = max_txns
    if BLOCKCYPHER_API_KEY:
        params['token'] = BLOCKCYPHER_API_KEY

    r = requests.get(url_to_hit, params=params, verify=True)

    return json.loads(r.text)


def get_transactions_details(tx_hash, coin_symbol='btc'):

    assert is_valid_tx_hash(tx_hash)

    url_to_hit = 'https://api.blockcypher.com/v1/%s/%s/txs/%s' % (
            COIN_SYMBOL_MAPPINGS[coin_symbol][1],
            COIN_SYMBOL_MAPPINGS[coin_symbol][2],
            tx_hash)

    print(url_to_hit)

    params = {}
    if BLOCKCYPHER_API_KEY:
        params['token'] = BLOCKCYPHER_API_KEY

    r = requests.get(url_to_hit, params=params, verify=True)

    response_dict = json.loads(r.text)

    # format this string as a datetime object
    if response_dict['block_height'] > 0:
        response_dict['confirmed'] = parser.parse(response_dict['confirmed'])
        response_dict['received'] = parser.parse(response_dict['received'])
    else:
        # Blockcypher reports fake times if it's not in a block
        response_dict['confirmed'] = None
        response_dict['block_height'] = None

    return response_dict


def get_block_details(block_representation, coin_symbol='btc', max_txns=None):
    """
    block_representation may be the block number of block hash
    """

    # assert is_valid_block_representation(block_representation)

    url_to_hit = 'https://api.blockcypher.com/v1/%s/%s/blocks/%s' % (
            COIN_SYMBOL_MAPPINGS[coin_symbol][1],
            COIN_SYMBOL_MAPPINGS[coin_symbol][2],
            block_representation)

    # print(url_to_hit)

    params = {}
    if BLOCKCYPHER_API_KEY:
        params['token'] = BLOCKCYPHER_API_KEY
    if max_txns:
        params['limit'] = max_txns

    r = requests.get(url_to_hit, params=params, verify=True)

    response_dict = json.loads(r.text)

    if response_dict.get('confirmed'):
        response_dict['confirmed'] = parser.parse(response_dict['confirmed'])

    return response_dict
