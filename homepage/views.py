from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from annoying.decorators import render_to
from blockexplorer.decorators import assert_valid_coin_symbol

from homepage.forms import SearchForm

from blockcypher.api import get_transaction_details, get_block_overview, get_latest_block_height
from blockcypher.utils import is_valid_hash, is_valid_block_num, is_valid_sha_block_hash, is_valid_address
from blockcypher.constants import SHA_COINS, SCRYPT_COINS, COIN_SYMBOL_MAPPINGS


@render_to('home.html')
def home(request):
    form = SearchForm(initial={
        'search_string': '16Fg2yjwrbtC6fZp61EV9mNVKmwCzGasw5',
        'coin_symbol': 'btc',
        })
    if request.method == 'POST':
        form = SearchForm(data=request.POST)
        if form.is_valid():
            redirect_url = None
            search_string = form.cleaned_data['search_string']
            coin_symbol = form.cleaned_data['coin_symbol']
            kwargs = {'coin_symbol': coin_symbol}
            if is_valid_block_num(search_string):
                kwargs['block_representation'] = search_string
                redirect_url = reverse('block_overview', kwargs=kwargs)
            elif is_valid_hash(search_string):
                if coin_symbol in SHA_COINS:
                    if is_valid_sha_block_hash(search_string):
                        kwargs['block_representation'] = search_string
                        redirect_url = reverse('block_overview', kwargs=kwargs)
                    else:
                        kwargs['tx_hash'] = search_string
                        redirect_url = reverse('transaction_overview', kwargs=kwargs)
                elif coin_symbol in SCRYPT_COINS:
                    # Try to see if it's a valid TX hash
                    tx_details = get_transaction_details(
                            tx_hash=search_string,
                            coin_symbol=coin_symbol,
                            limit=1,
                            )
                    if 'error' in tx_details:
                        # Not a valid TX hash, see if it's a block hash by checking blockchain
                        block_details = get_block_overview(
                                block_representation=search_string,
                                coin_symbol=coin_symbol,
                                txn_limit=1,
                                )
                        if 'error' in block_details:
                            msg = _("Sorry, that's not a valid transaction or block hash for %(currency)s" % {'currency': coin_symbol})
                            messages.error(request, msg)
                        else:
                            kwargs['block_representation'] = search_string
                            redirect_url = reverse('block_overview', kwargs=kwargs)
                    else:
                        kwargs['tx_hash'] = search_string
                        redirect_url = reverse('transaction_overview', kwargs=kwargs)

            elif is_valid_address(search_string):
                # It's an address
                kwargs['address'] = search_string
                first_char = search_string[0]
                # Override coin_symbol if we can infer it from the blockchain
                # TODO: find multisig prefixes for altcoins
                if first_char in ('1', '3'):
                    # Do not force addresses starting with 3 to be BTC because that's also used by litecoin
                    kwargs['coin_symbol'] = 'btc'
                elif first_char in ('m', '2'):
                    # Note that addresses starting in 2 can be LTC testnet, but since we don't support that it's okay to include
                    kwargs['coin_symbol'] = 'btc-testnet'
                elif first_char in ('D', ):
                    kwargs['coin_symbol'] = 'doge'
                elif first_char in ('L', ):
                    kwargs['coin_symbol'] = 'ltc'
                elif first_char in ('U', ):
                    kwargs['coin_symbol'] = 'uro'
                elif first_char in ('C', ):
                    kwargs['coin_symbol'] = 'bcy'

                redirect_url = reverse('address_overview', kwargs=kwargs)

            if redirect_url:
                return HttpResponseRedirect(redirect_url)

        else:
            currency = COIN_SYMBOL_MAPPINGS[request.POST['coin_symbol']]['display_shortname']
            msg = _("Sorry, that's not a valid %(currency)s address, transaction or block" % {
                'currency': currency})
            messages.error(request, msg)

    return {
        'is_home': True,
        'form': form
    }


@assert_valid_coin_symbol
@render_to('coin_overview.html')
def coin_overview(request, coin_symbol):

    initial = {
            'coin_symbol': coin_symbol,
            'search_string': COIN_SYMBOL_MAPPINGS[coin_symbol]['example_address']
            }
    form = SearchForm(initial=initial)

    latest_bh = get_latest_block_height(coin_symbol=coin_symbol)

    recent_blocks = [get_block_overview(block_height, coin_symbol=coin_symbol, txn_limit=1) for block_height in reversed(range(latest_bh-4, latest_bh+1))]
    #import pprint; pprint.pprint(recent_blocks, width=1)

    return {
            'coin_symbol': coin_symbol,
            'form': form,
            'recent_blocks': recent_blocks,
            }


def fail500(request):
    raise Exception('IntentionalFail: This Was On Purpose')
