# Copied 2014-09-24 from http://rosettacode.org/wiki/Bitcoin/address_validation#Python

from hashlib import sha256

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
