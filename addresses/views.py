from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from annoying.decorators import render_to

from blockcypher import get_address_details


@render_to('address_overview.html')
def address_overview(request, coin_symbol, address):

    # TODO: this doesn't cover pagination >500 and will fail silently-ish on those cases!
    address_details = get_address_details(address=address, coin_symbol=coin_symbol, max_txns=500)

    # import pprint; pprint.pprint(address_details, width=1)

    if 'error' in address_details:
        msg = _('Sorry, that address was not found')
        messages.warning(request, msg)
        return HttpResponseRedirect(reverse('home'))

    confirmed_transactions = address_details.get('txrefs', [])
    unconfirmed_transactions = address_details.get('unconfirmed_txrefs', [])

    all_transactions = unconfirmed_transactions + confirmed_transactions

    # doesn't cover pagination
    confirmed_sent_satoshis, confirmed_recieved_satoshis = 0, 0
    unconfirmed_sent_satoshis, unconfirmed_recieved_satoshis = 0, 0
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
                confirmed_recieved_satoshis += transaction['value']
            else:
                unconfirmed_recieved_satoshis += transaction['value']

    return {
            'coin_symbol': coin_symbol,
            'address': address,
            'confirmed_sent_satoshis': confirmed_sent_satoshis,
            'unconfirmed_sent_satoshis': unconfirmed_sent_satoshis,
            'total_sent_satoshis': unconfirmed_sent_satoshis + confirmed_sent_satoshis,
            'confirmed_recieved_satoshis': confirmed_recieved_satoshis,
            'unconfirmed_recieved_satoshis': unconfirmed_recieved_satoshis,
            'total_recieved_satoshis': unconfirmed_recieved_satoshis + confirmed_recieved_satoshis,
            'unconfirmed_balance_satoshis': address_details['unconfirmed_balance'],
            'confirmed_balance_satoshis': address_details['balance'],
            'total_balance_satoshis': address_details['final_balance'],
            'all_transactions': all_transactions,
            'num_confirmed_txns': address_details['n_tx'],
            'num_unconfirmed_txns': address_details['unconfirmed_n_tx'],
            'num_all_txns': address_details['final_n_tx'],
            'has_more': address_details.get('hasMore'),
            }
