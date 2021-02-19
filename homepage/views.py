from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from annoying.decorators import render_to
from blockexplorer.decorators import assert_valid_coin_symbol

from blockexplorer.settings import BLOCKCYPHER_PUBLIC_KEY, BLOCKCYPHER_API_KEY
from blockexplorer.walletname import lookup_wallet_name, is_valid_wallet_name

from homepage.forms import SearchForm, UnitChoiceForm

from blockcypher.api import get_transaction_details, get_block_overview, get_blocks_overview, get_latest_block_height, get_broadcast_transactions, get_blockchain_fee_estimates
from blockcypher.utils import is_valid_hash, is_valid_ethash_block_hash, is_valid_block_num, is_valid_sha_block_hash, is_valid_address, is_valid_eth_address
from blockcypher.constants import ETHASH_COINS, SHA_COINS, SCRYPT_COINS, COIN_SYMBOL_MAPPINGS

from operator import itemgetter


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
                            api_key=BLOCKCYPHER_API_KEY,
                            )
                    if 'error' in tx_details:
                        # Not a valid TX hash, see if it's a block hash by checking blockchain
                        block_details = get_block_overview(
                                block_representation=search_string,
                                coin_symbol=coin_symbol,
                                txn_limit=1,
                                api_key=BLOCKCYPHER_API_KEY,
                                )
                        if 'error' in block_details:
                            msg = _("Sorry, '%(search_string)s' is not a valid transaction or block hash for %(currency)s" % {
                                'currency': coin_symbol,
                                'search_string': search_string,
                                })
                            messages.error(request, msg)
                        else:
                            kwargs['block_representation'] = search_string
                            redirect_url = reverse('block_overview', kwargs=kwargs)
                    else:
                        kwargs['tx_hash'] = search_string
                        redirect_url = reverse('transaction_overview', kwargs=kwargs)

                elif coin_symbol in ETHASH_COINS:
                    # Try to see if it's a valid TX hash
                    tx_details = get_transaction_details(
                            tx_hash=search_string,
                            coin_symbol=coin_symbol,
                            limit=1,
                            api_key=BLOCKCYPHER_API_KEY,
                            )
                    if 'error' in tx_details:
                        # Not a valid TX hash, see if it's a block hash by checking blockchain
                        block_details = get_block_overview(
                                block_representation=search_string,
                                coin_symbol=coin_symbol,
                                txn_limit=1,
                                api_key=BLOCKCYPHER_API_KEY,
                                )
                        if 'error' in block_details:
                            msg = _("Sorry, '%(search_string)s' is not a valid transaction or block hash for %(currency)s" % {
                                'currency': coin_symbol,
                                'search_string': search_string,
                                })
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
                # Look first for bech32 address
                if search_string.startswith('bc1'):
                    kwargs['coin_symbol'] = 'btc'
                elif search_string.startswith('ltc1'):
                    kwargs['coin_symbol'] = 'ltc'
                elif search_string.startswith('tb1'):
                    kwargs['coin_symbol'] = 'btc-testnet'
                elif search_string.startswith('bcy1'):
                    kwargs['coin_symbol'] = 'bcy'
                    print(kwargs)
                else:
                    # After look at first char
                    first_char = search_string[0]
                    # Override coin_symbol if we can infer it from the blockchain
                    # There is now generic constants in the python library (constants.py)
                    # Not migrating because this is custom (those constants have overlap/ambiguity)
                    if first_char in ('1', 'b', ):
                        # Do not force addresses starting with 3 to be BTC because that's also used by LTC
                        kwargs['coin_symbol'] = 'btc'
                    elif first_char in ('m', 'n', '2', 't', ):
                        # Note that addresses starting in 2 can be LTC testnet, but since we don't support that it's okay to include
                        kwargs['coin_symbol'] = 'btc-testnet'
                    elif first_char in ('9', 'A', 'D',):
                        kwargs['coin_symbol'] = 'doge'
                    elif first_char in ('X', '7'):
                        kwargs['coin_symbol'] = 'dash'
                    elif first_char in ('L', 'l','M', ):
                        # Do not force addresses starting with 3 to be LTC because that's also used by BTC
                        kwargs['coin_symbol'] = 'ltc'
                    elif first_char in ('B', 'C'):
                        kwargs['coin_symbol'] = 'bcy'
                redirect_url = reverse('address_overview', kwargs=kwargs)
            elif is_valid_eth_address(search_string):
                    # It's an address
                    kwargs['address'] = search_string
                    kwargs['coin_symbol'] = 'eth'
                    redirect_url = reverse('address_overview', kwargs=kwargs)

            elif is_valid_wallet_name(search_string):
                addr = lookup_wallet_name(search_string, kwargs['coin_symbol'])
                if addr:
                    kwargs['address'] = addr
                    kwargs['wallet_name'] = search_string
                    redirect_url = reverse('address_overview', kwargs=kwargs)
                else:
                    msg = _("Sorry, that's not a valid wallet name")
                    messages.error(request, msg)

            if redirect_url:
                return HttpResponseRedirect(redirect_url)

        else:
            currency = COIN_SYMBOL_MAPPINGS[request.POST['coin_symbol']]['display_shortname']
            msg = _("Sorry, '%(search_string)s' is not a valid %(currency)s address, wallet name, transaction or block" % {
                'currency': currency,
                'search_string': request.POST['search_string'],
                })
            messages.error(request, msg)

    return {
        'is_home': True,
        'form': form,
        'is_input_page': True,
    }


@assert_valid_coin_symbol
@render_to('coin_overview.html')
def coin_overview(request, coin_symbol):

    initial = {
            'coin_symbol': coin_symbol,
            'search_string': COIN_SYMBOL_MAPPINGS[coin_symbol]['example_address']
            }
    form = SearchForm(initial=initial)

    latest_bh = get_latest_block_height(coin_symbol=coin_symbol, api_key=BLOCKCYPHER_API_KEY)

    recent_blocks = get_blocks_overview(
            block_representation_list=list(reversed(range(latest_bh-4, latest_bh+1))),
            coin_symbol=coin_symbol,
            api_key=BLOCKCYPHER_API_KEY)

    recent_blocks = sorted(recent_blocks, key=lambda k: k['height'], reverse=True)
    fees = get_blockchain_fee_estimates(coin_symbol=coin_symbol, api_key=BLOCKCYPHER_API_KEY)

    fees['high_fee_per_kb__smalltx'] = fees['high_fee_per_kb']/4
    fees['medium_fee_per_kb__smalltx'] = fees['medium_fee_per_kb']/4
    fees['low_fee_per_kb__smalltx'] = fees['low_fee_per_kb']/4
    # import pprint; pprint.pprint(recent_blocks, width=1)

    recent_txs = get_broadcast_transactions(coin_symbol=coin_symbol,
            api_key=BLOCKCYPHER_API_KEY,
            limit=10)

    recent_txs_filtered = []
    tx_hashes_seen = set([])
    for recent_tx in recent_txs:
        if recent_tx['hash'] in tx_hashes_seen:
            continue
        else:
            tx_hashes_seen.add(recent_tx['hash'])
            recent_txs_filtered.append(recent_tx)

    # sort recent txs by order (they're not always returning in order)
    recent_txs_filtered = sorted(recent_txs_filtered, key=itemgetter('received'), reverse=True)

    fee_api_url = 'https://api.blockcypher.com/v1/%s/%s' % (
            COIN_SYMBOL_MAPPINGS[coin_symbol]['blockcypher_code'],
            COIN_SYMBOL_MAPPINGS[coin_symbol]['blockcypher_network'],
            )

    return {
            'coin_symbol': coin_symbol,
            'form': form,
            'recent_blocks': recent_blocks,
            'recent_txs': recent_txs_filtered,
            'fees': fees,
            'fee_api_url': fee_api_url,
            'BLOCKCYPHER_PUBLIC_KEY': BLOCKCYPHER_PUBLIC_KEY,
            }


def set_units(request):
    if request.method == 'POST':
        form = UnitChoiceForm(data=request.POST)
        if form.is_valid():
            unit_choice = form.cleaned_data['unit_choice']
            request.session['user_units'] = unit_choice
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@render_to('highlights.html')
def highlights(request):
    return {}


def fail500(request):
    raise Exception('IntentionalFail: This Was On Purpose')
