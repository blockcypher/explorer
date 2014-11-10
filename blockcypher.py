from blockexplorer.settings import BLOCKCYPHER_API_KEY

from bitcoins.utils import is_valid_address, is_valid_tx_hash, is_valid_sha_block_representation, is_valid_scrypt_block_representation

from dateutil import parser

import requests
import json


COIN_SYMBOL_MAPPINGS = {
        # format like such
        # 'coin_symbol': ('Display Name', 'Blockcypher Code', 'Blockcypher Network', 'Currency Name/Abbrev', 'POW'),
        'btc': ('Bitcoin', 'btc', 'main', 'BTC', 'sha'),
        'btc-testnet': ('Bitcoin Testnet', 'btc', 'test3', 'BTC', 'sha'),
        'ltc': ('Litecoin', 'ltc', 'main', 'LTC', 'scrypt'),
        'uro': ('Uro', 'uro', 'main', 'URO', 'sha'),
        'bcy': ('BlockCypher Testnet', 'bcy', 'test', 'BCY', 'sha'),
        }

# TODO: DRY this out (but maintain order for dropdown)
COIN_SYMBOL_ORDER_LIST = ('btc', 'btc-testnet', 'ltc', 'uro', 'bcy')

SHA_COINS, SCRYPT_COINS = [], []
for coin_symbol in COIN_SYMBOL_MAPPINGS:
    if COIN_SYMBOL_MAPPINGS[coin_symbol][4] == 'sha':
        SHA_COINS.append(coin_symbol)
    elif COIN_SYMBOL_MAPPINGS[coin_symbol][4] == 'scrypt':
        SCRYPT_COINS.append(coin_symbol)
    else:
        raise Exception('Logic Error: Not Possible')

# Django-Style List
COIN_CHOICES = []
for coin_symbol in COIN_SYMBOL_ORDER_LIST:
    COIN_CHOICES.append((coin_symbol, COIN_SYMBOL_MAPPINGS[coin_symbol][0]))


def get_address_details(address, coin_symbol='btc', max_txns=None):

    # This check appears to work for other blockchains
    # TODO: verify and/or improve
    assert is_valid_address(address)

    url_to_hit = 'https://api.blockcypher.com/v1/%s/%s/addrs/%s' % (
            COIN_SYMBOL_MAPPINGS[coin_symbol][1],
            COIN_SYMBOL_MAPPINGS[coin_symbol][2],
            address)

    #print(url_to_hit)

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
            tx_hash,
            )

    #print(url_to_hit)

    params = {}
    if BLOCKCYPHER_API_KEY:
        params['token'] = BLOCKCYPHER_API_KEY

    r = requests.get(url_to_hit, params=params, verify=True)

    response_dict = json.loads(r.text)

    if not 'error' in response_dict:
        if response_dict['block_height'] > 0:
            response_dict['confirmed'] = parser.parse(response_dict['confirmed'])
        else:
            # Blockcypher reports fake times if it's not in a block
            response_dict['confirmed'] = None
            response_dict['block_height'] = None

        # format this string as a datetime object
        response_dict['received'] = parser.parse(response_dict['received'])

    return response_dict


def get_block_details(block_representation, coin_symbol='btc', max_txns=None):
    """
    block_representation may be the block number of block hash
    """

    # defensive checks
    if coin_symbol in SHA_COINS:
        assert is_valid_sha_block_representation(block_representation)
    elif coin_symbol in SCRYPT_COINS:
        assert is_valid_scrypt_block_representation(block_representation)

    url_to_hit = 'https://api.blockcypher.com/v1/%s/%s/blocks/%s' % (
            COIN_SYMBOL_MAPPINGS[coin_symbol][1],
            COIN_SYMBOL_MAPPINGS[coin_symbol][2],
            block_representation,
            )

    #print(url_to_hit)

    params = {}
    if BLOCKCYPHER_API_KEY:
        params['token'] = BLOCKCYPHER_API_KEY
    if max_txns:
        params['limit'] = max_txns

    r = requests.get(url_to_hit, params=params, verify=True)

    response_dict = json.loads(r.text)

    if response_dict.get('received_time'):
        response_dict['received_time'] = parser.parse(response_dict['received_time'])

    return response_dict


def get_latest_block_height(coin_symbol):

    url_to_hit = 'https://api.blockcypher.com/v1/%s/%s/' % (
            COIN_SYMBOL_MAPPINGS[coin_symbol][1],
            COIN_SYMBOL_MAPPINGS[coin_symbol][2],
            )

    #print(url_to_hit)

    params = {}
    if BLOCKCYPHER_API_KEY:
        params['token'] = BLOCKCYPHER_API_KEY

    r = requests.get(url_to_hit, params=params, verify=True)

    response_dict = json.loads(r.text)

    return response_dict['height']
