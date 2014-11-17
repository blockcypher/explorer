from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from annoying.decorators import render_to

from blockcypher import get_address_details, get_address_url


@render_to('address_overview.html')
def address_overview(request, coin_symbol, address):

    TXNS_PER_PAGE = 50

    # 1 indexed page
    current_page = request.GET.get('page')
    if current_page:
        current_page = int(current_page)
    else:
        current_page = 1

    address_details = get_address_details(
            address=address,
            coin_symbol=coin_symbol,
            txn_limit=TXNS_PER_PAGE,
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

    api_url = get_address_url(coin_symbol=coin_symbol, address=address)

    return {
            'coin_symbol': coin_symbol,
            'address': address,
            'api_url': api_url,
            'current_page': current_page,
            'max_pages': max(address_details['final_n_tx'] // TXNS_PER_PAGE, 1),
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
            'has_more': address_details.get('hasMore'),
            }
