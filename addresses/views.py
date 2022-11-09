from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_exempt

from annoying.decorators import render_to

from blockexplorer.decorators import assert_valid_coin_symbol

from blockexplorer.settings import BLOCKCYPHER_PUBLIC_KEY, BLOCKCYPHER_API_KEY, BASE_URL

from blockcypher.api import get_address_full, get_address_overview
from blockcypher.constants import COIN_SYMBOL_MAPPINGS

from addresses.forms import AddressSearchForm

SMALL_PAYMENTS_MSG = '''
Please note that for very small payments of 100 bits or less,
the payment will not forward as the amount to forward is lower than the mining fee.
'''

# http://www.useragentstring.com/pages/Crawlerlist/
BOT_LIST = (
        'googlebot',
        'bingbot',
        'baiduspider',
        'yandexbot',
        'omniexplorer_bot',
        )


def is_bot(user_agent):
    if user_agent:
        user_agent_lc = user_agent.lower()
        for bot_string in BOT_LIST:
            if bot_string in user_agent_lc:
                return True
    return False


@assert_valid_coin_symbol
@render_to('address_overview.html')
def address_overview(request, coin_symbol, address, wallet_name=None):
    TXNS_PER_PAGE = 10

    if request.GET.get('page'):
        # get rid of old pagination (for googlebot)
        kwargs = {'coin_symbol': coin_symbol, 'address': address}
        return HttpResponseRedirect(reverse('address_overview', kwargs=kwargs))

    before_bh = request.GET.get('before')

    try:
        user_agent = request.META.get('HTTP_USER_AGENT')

        if is_bot(user_agent):
            # very crude hack!
            confirmations = 1
        else:
            confirmations = 0

        address_details = get_address_full(
                address=address,
                coin_symbol=coin_symbol,
                txn_limit=TXNS_PER_PAGE,
                inout_limit=5,
                confirmations=confirmations,
                api_key=BLOCKCYPHER_API_KEY,
                before_bh=before_bh,
                )
    except AssertionError:
        msg = _('Invalid Address')
        messages.warning(request, msg)
        redir_url = reverse('coin_overview', kwargs={'coin_symbol': coin_symbol})
        return HttpResponseRedirect(redir_url)

    # import pprint; pprint.pprint(address_details, width=1)

    if 'error' in address_details:
        msg = _('Sorry, that address was not found')
        messages.warning(request, msg)
        return HttpResponseRedirect(reverse('home'))

    all_transactions = address_details.get('txs', [])
    # import pprint; pprint.pprint(all_transactions, width=1)

    api_url = 'https://api.blockcypher.com/v1/%s/%s/addrs/%s/full?limit=50' % (
            COIN_SYMBOL_MAPPINGS[coin_symbol]['blockcypher_code'],
            COIN_SYMBOL_MAPPINGS[coin_symbol]['blockcypher_network'],
            address)

    return {
            'coin_symbol': coin_symbol,
            'address': address,
            'api_url': api_url,
            'wallet_name': wallet_name,
            'has_more': address_details.get('hasMore', False),
            'total_sent_satoshis': address_details['total_sent'],
            'total_received_satoshis': address_details['total_received'],
            'unconfirmed_balance_satoshis': address_details['unconfirmed_balance'],
            'confirmed_balance_satoshis': address_details['balance'],
            'total_balance_satoshis': address_details['final_balance'],
            'flattened_txs': all_transactions,
            'before_bh': before_bh,
            'num_confirmed_txns': address_details['n_tx'],
            'num_unconfirmed_txns': address_details['unconfirmed_n_tx'],
            'num_all_txns': address_details['final_n_tx'],
            'BLOCKCYPHER_PUBLIC_KEY': BLOCKCYPHER_PUBLIC_KEY,
            }

@xframe_options_exempt
@render_to('balance_widget.html')
def render_balance_widget(request, coin_symbol, address):
    address_overview = get_address_overview(address=address,
            coin_symbol=coin_symbol, api_key=BLOCKCYPHER_API_KEY)
    return {
            'address_overview': address_overview,
            'coin_symbol': coin_symbol,
            'b58_address': address,
            'BASE_URL': BASE_URL,
            }


@xframe_options_exempt
@render_to('received_widget.html')
def render_received_widget(request, coin_symbol, address):
    address_overview = get_address_overview(address=address,
            coin_symbol=coin_symbol, api_key=BLOCKCYPHER_API_KEY)
    return {
            'address_overview': address_overview,
            'coin_symbol': coin_symbol,
            'b58_address': address,
            'BASE_URL': BASE_URL,
            }


@render_to('search_widgets.html')
def search_widgets(request, coin_symbol):
    form = AddressSearchForm()
    if request.method == 'POST':
        form = AddressSearchForm(data=request.POST)
        if form.is_valid():
            kwargs = {
                    'coin_symbol': form.cleaned_data['coin_symbol'],
                    'address': form.cleaned_data['coin_address'],
                    }
            redir_url = reverse('widgets_overview', kwargs=kwargs)
            return HttpResponseRedirect(redir_url)
    elif request.method == 'GET':
        new_coin_symbol = request.GET.get('c')
        if new_coin_symbol:
            initial = {'coin_symbol': new_coin_symbol}
            form = AddressSearchForm(initial=initial)

    return {
            'form': form,
            'coin_symbol': coin_symbol,
            'is_input_page': True,
            }


@render_to('widgets.html')
def widgets_overview(request, coin_symbol, address):
    return {
            'coin_symbol': coin_symbol,
            'b58_address': address,
            'BASE_URL': BASE_URL,
            }


def widget_forwarding(request):
    kwargs = {'coin_symbol': 'btc'}
    redir_url = reverse('search_widgets', kwargs=kwargs)
    return HttpResponseRedirect(redir_url)
