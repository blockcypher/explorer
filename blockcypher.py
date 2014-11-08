from blockexplorer.settings import BLOCKCYPHER_API_KEY

from bitcoins.address import is_valid_btc_address
from bitcoins.transaction import is_valid_tx_hash

from dateutil import parser

import requests
import json


def get_address_details(btc_address):

    BASE_URL = 'https://api.blockcypher.com/v1/btc/main/addrs'

    assert is_valid_btc_address(btc_address)

    url_to_hit = '%s/%s' % (BASE_URL, btc_address)

    if BLOCKCYPHER_API_KEY:
        BASE_URL += '?token=%s' % BLOCKCYPHER_API_KEY

    r = requests.get(url_to_hit)

    return json.loads(r.text)


def get_transactions_details(tx_hash):

    BASE_URL = 'https://api.blockcypher.com/v1/btc/main/txs'

    assert is_valid_tx_hash(tx_hash)

    url_to_hit = '%s/%s' % (BASE_URL, tx_hash)

    if BLOCKCYPHER_API_KEY:
        BASE_URL += '?token=%s' % BLOCKCYPHER_API_KEY

    r = requests.get(url_to_hit)

    response_dict = json.loads(r.text)

    # format this string as a datetime object
    response_dict['confirmed'] = parser.parse(response_dict['confirmed'])

    return response_dict
