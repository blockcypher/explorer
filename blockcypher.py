from blockexplorer.settings import BLOCKCYPHER_API_KEY

from bitcoins.utils import is_valid_address, is_valid_hash, is_valid_sha_block_representation, is_valid_scrypt_block_representation, is_valid_block_num

from dateutil import parser

import requests
import json


# Ordered List of Coin Symbol Dictionaries
COIN_SYMBOL_ODICT_LIST = [
        {
            'coin_symbol': 'btc',
            'display_name': 'Bitcoin',
            'display_shortname': 'BTC',
            'blockcypher_code': 'btc',
            'blockcypher_network': 'main',
            'currency_abbrev': 'BTC',
            'pow': 'sha',
            'example_address': '16Fg2yjwrbtC6fZp61EV9mNVKmwCzGasw5',
            },
        {
            'coin_symbol': 'btc-testnet',
            'display_name': 'Bitcoin Testnet',
            'display_shortname': 'BTC Testnet',
            'blockcypher_code': 'btc',
            'blockcypher_network': 'test3',
            'currency_abbrev': 'BTC',
            'pow': 'sha',
            'example_address': '2N1rjhumXA3ephUQTDMfGhufxGQPZuZUTMk',
            },
        {
            'coin_symbol': 'ltc',
            'display_name': 'Litecoin',
            'display_shortname': 'LTC',
            'blockcypher_code': 'ltc',
            'blockcypher_network': 'main',
            'currency_abbrev': 'LTC',
            'pow': 'scrypt',
            'example_address': 'LcFFkbRUrr8j7TMi8oXUnfR4GPsgcXDepo',
            },
        {
            'coin_symbol': 'doge',
            'display_name': 'Dogecoin',
            'display_shortname': 'DOGE',
            'blockcypher_code': 'doge',
            'blockcypher_network': 'main',
            'currency_abbrev': 'DOGE',
            'pow': 'scrypt',
            'example_address': 'D7Y55r6Yoc1G8EECxkQ6SuSjTgGJJ7M6yD',
            },
        {
            'coin_symbol': 'uro',
            'display_name': 'Uro',
            'display_shortname': 'URO',
            'blockcypher_code': 'uro',
            'blockcypher_network': 'main',
            'currency_abbrev': 'URO',
            'pow': 'sha',
            'example_address': 'Uhf1LGdgmWe33hB9VVtubyzq1GduUAtaAJ',
            },
        {
            'coin_symbol': 'bcy',
            'display_name': 'BlockCypher Testnet',
            'display_shortname': 'BC Testnet',
            'blockcypher_code': 'bcy',
            'blockcypher_network': 'test',
            'currency_abbrev': 'BCY',
            'pow': 'sha',
            'example_address': 'CFr99841LyMkyX5ZTGepY58rjXJhyNGXHf',
            },
        ]

# all fields required
REQUIRED_FIELDS = (
    'coin_symbol',  # this is a made up unique symbole for internal use only
    'display_name',  # what it commonly looks like
    'display_shortname',  # an abbreviated version of display_name for when space is tight
    'blockcypher_code',  # the blockcypher unique ID for their URLs
    'blockcypher_network',  # the blockcypher network (main/test)
    'currency_abbrev',  # what the unit of currency looks like when abbreviated
    'pow',  # the proof of work algorithm
    'example_address',  # an example address
    )

# Make sure no fields are missing
for coin_symbol_dict in COIN_SYMBOL_ODICT_LIST:
    for required_field in REQUIRED_FIELDS:
        assert required_field in coin_symbol_dict


COIN_SYMBOL_LIST = [x['coin_symbol'] for x in COIN_SYMBOL_ODICT_LIST]
SHA_COINS = [x['coin_symbol'] for x in COIN_SYMBOL_ODICT_LIST if x['pow'] == 'sha']
SCRYPT_COINS = [x['coin_symbol'] for x in COIN_SYMBOL_ODICT_LIST if x['pow'] == 'scrypt']

# For django-style lists
COIN_CHOICES = []
for coin_symbol_dict in COIN_SYMBOL_ODICT_LIST:
    COIN_CHOICES.append((coin_symbol_dict['coin_symbol'], coin_symbol_dict['display_name']))

# mappings (similar to above but for when order doens't matter)
COIN_SYMBOL_MAPPINGS = {}
for coin_symbol_dict in COIN_SYMBOL_ODICT_LIST:
    coin_symbol = coin_symbol_dict.pop('coin_symbol')
    COIN_SYMBOL_MAPPINGS[coin_symbol] = coin_symbol_dict


def get_address_url(coin_symbol, address):
    assert(coin_symbol)

    return 'https://api.blockcypher.com/v1/%s/%s/addrs/%s' % (
        COIN_SYMBOL_MAPPINGS[coin_symbol]['blockcypher_code'],
        COIN_SYMBOL_MAPPINGS[coin_symbol]['blockcypher_network'],
        address)


def get_address_details(address, coin_symbol='btc', max_txns=None):

    # This check appears to work for other blockchains
    # TODO: verify and/or improve
    assert is_valid_address(address)

    url = get_address_url(coin_symbol=coin_symbol, address=address)

    print(url)

    params = {}
    if max_txns:
        params['limit'] = max_txns
    if BLOCKCYPHER_API_KEY:
        params['token'] = BLOCKCYPHER_API_KEY

    r = requests.get(url, params=params, verify=True)

    response_dict = json.loads(r.text)

    confirmed_txrefs = []
    for confirmed_txref in response_dict.get('txrefs', []):
        confirmed_txref['confirmed'] = parser.parse(confirmed_txref['confirmed'])
        confirmed_txrefs.append(confirmed_txref)
    response_dict['txrefs'] = confirmed_txrefs

    unconfirmed_txrefs = []
    for unconfirmed_txref in response_dict.get('unconfirmed_txrefs', []):
        unconfirmed_txref['received'] = parser.parse(unconfirmed_txref['received'])
        unconfirmed_txrefs.append(unconfirmed_txref)
    response_dict['unconfirmed_txrefs'] = unconfirmed_txrefs

    return response_dict


def get_transaction_url(tx_hash, coin_symbol):
    return 'https://api.blockcypher.com/v1/%s/%s/txs/%s' % (
            COIN_SYMBOL_MAPPINGS[coin_symbol]['blockcypher_code'],
            COIN_SYMBOL_MAPPINGS[coin_symbol]['blockcypher_network'],
            tx_hash,
            )


def get_transaction_details(tx_hash, coin_symbol='btc'):

    assert is_valid_hash(tx_hash)

    url = get_transaction_url(tx_hash=tx_hash, coin_symbol=coin_symbol)

    print(url)

    params = {}
    if BLOCKCYPHER_API_KEY:
        params['token'] = BLOCKCYPHER_API_KEY

    r = requests.get(url, params=params, verify=True)

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


def get_block_url(block_representation, coin_symbol):
    return 'https://api.blockcypher.com/v1/%s/%s/blocks/%s' % (
            COIN_SYMBOL_MAPPINGS[coin_symbol]['blockcypher_code'],
            COIN_SYMBOL_MAPPINGS[coin_symbol]['blockcypher_network'],
            block_representation,
            )


def get_block_details(block_representation, coin_symbol='btc', max_txns=None):
    """
    block_representation may be the block number of block hash
    """

    # defensive checks
    if coin_symbol in SHA_COINS:
        if coin_symbol == 'bcy':
            assert((is_valid_hash(block_representation) and block_representation[:4] == '0000') or is_valid_block_num(block_representation))
        else:
            assert is_valid_sha_block_representation(block_representation)
    elif coin_symbol in SCRYPT_COINS:
        assert is_valid_scrypt_block_representation(block_representation)

    url = get_block_url(block_representation=block_representation, coin_symbol=coin_symbol)

    print(url)

    params = {}
    if BLOCKCYPHER_API_KEY:
        params['token'] = BLOCKCYPHER_API_KEY
    if max_txns:
        params['limit'] = max_txns

    r = requests.get(url, params=params, verify=True)

    response_dict = json.loads(r.text)

    if response_dict.get('received_time'):
        response_dict['received_time'] = parser.parse(response_dict['received_time'])

    return response_dict


def get_blockchain_overview_url(coin_symbol):
    return 'https://api.blockcypher.com/v1/%s/%s/' % (
            COIN_SYMBOL_MAPPINGS[coin_symbol]['blockcypher_code'],
            COIN_SYMBOL_MAPPINGS[coin_symbol]['blockcypher_network'],
            )


def get_latest_block_height(coin_symbol):

    url = get_blockchain_overview_url(coin_symbol=coin_symbol)
    print(url)

    params = {}
    if BLOCKCYPHER_API_KEY:
        params['token'] = BLOCKCYPHER_API_KEY

    r = requests.get(url, params=params, verify=True)

    response_dict = json.loads(r.text)

    return response_dict['height']


def get_websocket_url(coin_symbol):

    assert coin_symbol

    return 'wss://socket.blockcypher.com/v1/%s/%s' % (
            COIN_SYMBOL_MAPPINGS[coin_symbol]['blockcypher_code'],
            COIN_SYMBOL_MAPPINGS[coin_symbol]['blockcypher_network'],
            )
