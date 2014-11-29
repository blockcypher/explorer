from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from annoying.decorators import render_to
from blockexplorer.decorators import assert_valid_coin_symbol

from blockexplorer.settings import BLOCKCYPHER_PUBLIC_KEY

from blockcypher.api import get_address_details, get_address_details_url


@assert_valid_coin_symbol
@render_to('address_overview.html')
def address_overview(request, coin_symbol, address):

    TXNS_PER_PAGE = 100

    # 1 indexed page
    current_page = request.GET.get('page')
    if current_page:
        current_page = int(current_page)
    else:
        current_page = 1

    address_details = get_address_details(
            address=address,
            coin_symbol=coin_symbol,
            txn_limit=5000,
            )

    #import pprint; pprint.pprint(address_details, width=1)

    if 'error' in address_details:
        msg = _('Sorry, that address was not found')
        messages.warning(request, msg)
        return HttpResponseRedirect(reverse('home'))

    all_transactions = address_details.get('unconfirmed_txrefs', []) + address_details.get('txrefs', [])

    # doesn't cover pagination
    confirmed_sent_satoshis, confirmed_received_satoshis = 0, 0
    unconfirmed_sent_satoshis, unconfirmed_received_satoshis = 0, 0
    for transaction in all_transactions:
        if transaction['tx_input_n'] >= 0:
            # It's sent
            if transaction['confirmations'] > 6:
                confirmed_sent_satoshis += transaction['value']
            else:
                unconfirmed_sent_satoshis += transaction['value']
        else:
            # It's received
            if transaction['confirmations'] > 6:
                confirmed_received_satoshis += transaction['value']
            else:
                unconfirmed_received_satoshis += transaction['value']

    # transaction pagination: 0-indexed and inclusive
    tx_start_num = (current_page - 1) * TXNS_PER_PAGE
    tx_end_num = current_page * TXNS_PER_PAGE - 1

    # filter address details for pagination. HACK!
    all_transactions = all_transactions[tx_start_num:tx_end_num]

    api_url = get_address_details_url(address=address, coin_symbol=coin_symbol)

    all_txids = set([tx['tx_hash'] for tx in all_transactions])

    return {
            'coin_symbol': coin_symbol,
            'address': address,
            'api_url': api_url,
            'current_page': current_page,
            'max_pages': address_details['final_n_tx'] // TXNS_PER_PAGE + 1,
            'confirmed_sent_satoshis': confirmed_sent_satoshis,
            'unconfirmed_sent_satoshis': unconfirmed_sent_satoshis,
            'total_sent_satoshis': unconfirmed_sent_satoshis + confirmed_sent_satoshis,
            'confirmed_received_satoshis': confirmed_received_satoshis,
            'unconfirmed_received_satoshis': unconfirmed_received_satoshis,
            'total_received_satoshis': unconfirmed_received_satoshis + confirmed_received_satoshis,
            'unconfirmed_balance_satoshis': address_details['unconfirmed_balance'],
            'confirmed_balance_satoshis': address_details['balance'],
            'total_balance_satoshis': address_details['final_balance'],
            'all_transactions': all_transactions,
            'num_confirmed_txns': address_details['n_tx'],
            'num_unconfirmed_txns': address_details['unconfirmed_n_tx'],
            'num_all_txns': address_details['final_n_tx'],
            'has_more': bool(len(all_txids) != address_details['final_n_tx']),
            'BLOCKCYPHER_PUBLIC_KEY': BLOCKCYPHER_PUBLIC_KEY,
            }
