from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from annoying.decorators import render_to

from blockcypher import get_block_details, get_latest_block_height


@render_to('block_overview.html')
def block_overview(request, coin_symbol, block_representation):

    # TODO: this doesn't cover pagination >500 and will fail silently-ish on those cases!
    block_details = get_block_details(
            block_representation=block_representation,
            coin_symbol=coin_symbol,
            max_txns=500)

    #import pprint; pprint.pprint(block_details, width=1)

    if 'error' in block_details:
        msg = _('Sorry, that block was not found')
        messages.warning(request, msg)
        return HttpResponseRedirect(reverse('home'))

    return {
            'coin_symbol': coin_symbol,
            'block_details': block_details,
            }


def latest_block(request, coin_symbol):
    latest_block_height = get_latest_block_height(coin_symbol=coin_symbol)
    kwargs = {
            'coin_symbol': coin_symbol,
            'block_representation': latest_block_height,
            }
    return HttpResponseRedirect(reverse('block_overview', kwargs=kwargs))
