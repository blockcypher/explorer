import re

from hashlib import sha256


SATOSHIS_PER_BTC = 10**8
SATOSHIS_PER_MILLIBITCOIN = 10**5

HASH_CHARS_RE = re.compile('^[0-9a-f]*$')


def satoshis_to_btc(satoshis, decimals=4):

    btc = float(satoshis) / float(SATOSHIS_PER_BTC)

    if decimals:
        return round(btc, decimals)
    else:
        return btc


def uses_only_hash_chars(string):
    return HASH_CHARS_RE.match(string)


def is_valid_hash(string):
    return len(string.strip()) == 64 and uses_only_hash_chars(string)


def is_valid_tx_hash(string):
    return is_valid_hash(string)


### Blocks ###

def is_valid_block_num(block_num):
    try:
        bn_as_int = int(block_num)
    except:
        return False

    # hackey approximation
    return 0 <= bn_as_int <= 10**8


def is_valid_block_hash(block_hash):
    return is_valid_hash(block_hash) and block_hash[:5] == '00000'


def is_valid_block_representation(block_representation):
    return is_valid_block_num(block_representation) or is_valid_block_hash(block_representation)


### Addresses ###

# Copied 2014-09-24 from http://rosettacode.org/wiki/Bitcoin/address_validation#Python

digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def decode_base58(bc, length):
    n = 0
    for char in bc:
        n = n * 58 + digits58.index(char)
    return n.to_bytes(length, 'big')


def btc_address_valid(bc):
    bcbytes = decode_base58(bc, 25)
    return bcbytes[-4:] == sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]


def is_valid_btc_address(b58_address):
    try:
        return btc_address_valid(b58_address)
    except:
        # handle edge cases like an address too long to decode
        return False
