from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from annoying.decorators import render_to
from blockexplorer.decorators import assert_valid_coin_symbol

from blockexplorer.settings import BLOCKCYPHER_API_KEY

from blockcypher.api import get_block_details, get_latest_block_height, get_block_overview, get_block_hash
from blockcypher.constants import COIN_SYMBOL_MAPPINGS
from blockcypher.utils import is_valid_hash

from utils import get_max_pages


@assert_valid_coin_symbol
@render_to('block_overview.html')
def block_overview(request, coin_symbol, block_representation):

    TXNS_PER_PAGE = 20

    # 1 indexed page
    current_page = request.GET.get('page')
    if current_page:
        current_page = int(current_page)
    else:
        current_page = 1

    # TODO: fail gracefully if the user picks a number of pages that is too large
    # Waiting on @matthieu's change to API first (currently throws 502)

    try:
        if not is_valid_hash(block_representation):
            # it's a block num, we want this as a hash
            block_hash = get_block_hash(
                    block_height=block_representation,
                    coin_symbol=coin_symbol,
                    api_key=BLOCKCYPHER_API_KEY,
                    )
            kwargs = {
                    'coin_symbol': coin_symbol,
                    'block_representation': block_hash,
                    }
            redir_url = reverse('block_overview', kwargs=kwargs)
            return HttpResponseRedirect(redir_url)

        block_details = get_block_details(
                block_representation=block_representation,
                coin_symbol=coin_symbol,
                txn_limit=TXNS_PER_PAGE,
                in_out_limit=25,
                txn_offset=(current_page-1)*TXNS_PER_PAGE,
                api_key=BLOCKCYPHER_API_KEY,
                )
    except AssertionError:
        msg = _('Invalid Block Representation')
        messages.warning(request, msg)
        redir_url = reverse('coin_overview', kwargs={'coin_symbol': coin_symbol})
        return HttpResponseRedirect(redir_url)

    # import pprint; pprint.pprint(block_details, width=1)

    if 'error' in block_details:
        msg = _('Sorry, that block was not found')
        messages.warning(request, msg)
        messages.warning(request, block_details['error'])
        return HttpResponseRedirect(reverse('home'))

    # Technically this is not the only API call used on this page
    api_url = 'https://api.blockcypher.com/v1/%s/%s/blocks/%s' % (
            COIN_SYMBOL_MAPPINGS[coin_symbol]['blockcypher_code'],
            COIN_SYMBOL_MAPPINGS[coin_symbol]['blockcypher_network'],
            block_representation,
            )

    return {
            'coin_symbol': coin_symbol,
            'api_url': api_url,
            'block_details': block_details,
            'current_page': current_page,
            'max_pages': get_max_pages(num_items=block_details['n_tx'], items_per_page=TXNS_PER_PAGE),
            }


def block_ordered_tx(request, coin_symbol, block_num, tx_num):

    block_overview = get_block_overview(
            block_representation=block_num,
            coin_symbol=coin_symbol,
            txn_limit=1,
            txn_offset=int(tx_num),
            api_key=BLOCKCYPHER_API_KEY,
            )
    txids = block_overview.get('txids')

    if txids:
        tx_hash = txids[0]
        msg = _('This is transaction <strong>%(tx_num)s</strong> in block <strong>%(block_num)s</strong> (<a href="%(permalink)s">permalink</a>).' % {
            'tx_num': tx_num,
            'block_num': block_num,
            'permalink': reverse('block_ordered_tx', kwargs={
                'coin_symbol': coin_symbol,
                'block_num': block_num,
                'tx_num': tx_num,
                }),
            })
        messages.info(request, msg, extra_tags='safe')

        kwargs = {
                'coin_symbol': coin_symbol,
                'tx_hash': tx_hash,
                }

        redir_uri = reverse('transaction_overview', kwargs=kwargs) + '#advanced-details'

        return HttpResponseRedirect(redir_uri)

    else:
        msg = _('Sorry, block <strong>%(block_num)s</strong> only has <strong>%(n_tx)s</strong> transactions' % {
            'block_num': block_num,
            'n_tx': block_overview['n_tx'],
            })
        messages.warning(request, msg, extra_tags='safe')

        kwargs = {
                'coin_symbol': coin_symbol,
                'block_representation': block_num,
                }
        return HttpResponseRedirect(reverse('block_overview', kwargs=kwargs))


@assert_valid_coin_symbol
def latest_block(request, coin_symbol):
    latest_block_height = get_latest_block_height(coin_symbol=coin_symbol,
            api_key=BLOCKCYPHER_API_KEY)
    kwargs = {
            'coin_symbol': coin_symbol,
            'block_representation': latest_block_height,
            }
    return HttpResponseRedirect(reverse('block_overview', kwargs=kwargs))


def latest_block_forwarding(request):
    return HttpResponseRedirect(reverse('latest_block', kwargs={
        'coin_symbol': 'btc',
        }))
