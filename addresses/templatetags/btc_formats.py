from django import template
from bitcoins.utils import satoshis_to_btc

from blockcypher import COIN_SYMBOL_MAPPINGS


register = template.Library()


@register.filter(name='satoshis_to_btc_rounded')
def satoshis_to_btc_rounded(satoshis):
    return satoshis_to_btc(satoshis=satoshis, decimals=4)


@register.filter(name='coin_symbol_to_display_name')
def coin_symbol_to_display_name(coin_symbol):
    return COIN_SYMBOL_MAPPINGS[coin_symbol][0]


@register.filter(name='coin_symbol_to_currency_name')
def coin_symbol_to_currency_name(coin_symbol):
    return COIN_SYMBOL_MAPPINGS[coin_symbol][3]
