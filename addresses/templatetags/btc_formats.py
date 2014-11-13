from django import template
from bitcoins.utils import satoshis_to_btc

from blockcypher import COIN_SYMBOL_MAPPINGS, get_websocket_address


register = template.Library()


@register.filter(name='satoshis_to_btc_rounded')
def satoshis_to_btc_rounded(satoshis):
    return satoshis_to_btc(satoshis=satoshis, decimals=4)


@register.filter(name='coin_symbol_to_display_name')
def coin_symbol_to_display_name(coin_symbol):
    return COIN_SYMBOL_MAPPINGS[coin_symbol]['display_name']


@register.filter(name='coin_symbol_to_currency_name')
def coin_symbol_to_currency_name(coin_symbol):
    return COIN_SYMBOL_MAPPINGS[coin_symbol]['currency_abbrev']


@register.filter(name='coin_symbol_to_wss')
def coin_symbol_to_wss(coin_symbol):
    return get_websocket_address(coin_symbol)
