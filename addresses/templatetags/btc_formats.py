from django import template
from bitcoins.utils import satoshis_to_btc

register = template.Library()


@register.filter(name='satoshis_to_btc_rounded')
def satoshis_to_btc_rounded(satoshis):
    return satoshis_to_btc(satoshis=satoshis, decimals=4)
