from django import template

from urllib.parse import urlencode, urlparse, urlunparse, parse_qs

from blockcypher.utils import format_crypto_units, estimate_satoshis_transacted
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


@register.assignment_tag
def estimate_satoshis_from_tx(txn_inputs, txn_outputs):
    return estimate_satoshis_transacted(inputs=txn_inputs, outputs=txn_outputs)


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


@register.simple_tag
def build_url(base_url, **query_params):
    """
    Entry point for the build_url template tag. This tag allows you to maintain
    a set of default querystring parameters and override an individual param.

    Inspired by https://djangosnippets.org/snippets/2332/ on 2015-10-26

    Usage:

        {% build_url base_url query_params %}

                  base_url: string variable -- the URL's prefix
                            try {% url some-url as base_url %}
              query_params: dictionary of default querystring values.
                            {'k1':'v1', 'k2':'mountain'}
                            -> ?k1=v1&k2=mountain
                  (output): (string) the url

    """
    # print('base_url', base_url)
    # print('query_params', query_params)

    url_parsed = urlparse(base_url)
    # print('url_parsed', url_parsed)

    qs_parsed = parse_qs(url_parsed.query)
    # print('qs_parsed', qs_parsed)

    new_qs = {}
    for key in qs_parsed:
        # parsing querystring returns a list entries (in case of dups)
        # crude deduplication here:
        new_qs[key] = qs_parsed[key][0]

    if query_params:
        for key in query_params:
            if query_params[key]:
                # only work if there is a value for that key (defensive)
                new_qs[key] = query_params[key]

    # print('new_qs', new_qs)

    return urlunparse(
            [
                url_parsed.scheme,
                url_parsed.netloc,
                url_parsed.path,
                url_parsed.params,
                urlencode(new_qs),
                url_parsed.fragment,
                ]
            )
