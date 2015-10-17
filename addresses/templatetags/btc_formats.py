from django import template

from blockcypher.utils import format_crypto_units
from blockcypher.api import _get_websocket_url
from blockcypher.constants import COIN_SYMBOL_MAPPINGS


register = template.Library()


@register.simple_tag(name='satoshis_to_user_units_trimmed')
def satoshis_to_user_units_trimmed(input_satoshis, user_unit='btc', coin_symbol='btc', print_cs=True, round_digits=0):
    return format_crypto_units(
            input_quantity=input_satoshis,
            input_type='satoshi',
            output_type=user_unit,
            coin_symbol=coin_symbol,
            print_cs=print_cs,
            safe_trimming=True,
            round_digits=round_digits,
            )


@register.filter(name='coin_symbol_to_display_name')
def coin_symbol_to_display_name(coin_symbol):
    return COIN_SYMBOL_MAPPINGS[coin_symbol]['display_name']


@register.filter(name='coin_symbol_to_display_shortname')
def coin_symbol_to_display_shortname(coin_symbol):
    return COIN_SYMBOL_MAPPINGS[coin_symbol]['display_shortname']


@register.filter(name='coin_symbol_to_currency_name')
def coin_symbol_to_currency_name(coin_symbol):
    return COIN_SYMBOL_MAPPINGS[coin_symbol]['currency_abbrev']


@register.filter(name='coin_symbol_to_wss')
def coin_symbol_to_wss(coin_symbol):
    return _get_websocket_url(coin_symbol)


@register.filter(name='txn_outputs_to_data_dict')
def txn_outputs_to_data_dict(txn_outputs):
    '''
    NOTE: Assumes each transaction can only have one null data output, which is not a strict requirement
    https://github.com/blockcypher/explorer/issues/150#issuecomment-143899714
    '''
    for txn_output in txn_outputs:
        if txn_output.get('data_hex') or txn_output.get('data_string'):
            return {
                    'data_hex': txn_output.get('data_hex'),
                    'data_string': txn_output.get('data_string'),
                    }
