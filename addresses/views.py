from annoying.decorators import render_to

from blockcypher import get_address_details


@render_to('address_overview.html')
def address_overview(request, btc_address):

    # FIXME: this doesn't cover pagination and will fail silently-ish on those cases!
    address_details = get_address_details(btc_address)

    confirmed_transactions = address_details['txrefs']
    unconfirmed_transactions = address_details.get('unconfirmed_txrefs', [])

    # import pprint; pprint.pprint(address_details, width=1)

    # doesn't cover pagination
    confirmed_sent_satoshis, confirmed_recieved_satoshis = 0, 0
    for confirmed_transaction in confirmed_transactions:
        if confirmed_transaction['tx_input_n'] >= 0:
            # TODO: confirm this logic
            confirmed_sent_satoshis += confirmed_transaction['value']
        else:
            confirmed_recieved_satoshis += confirmed_transaction['value']
    unconfirmed_sent_satoshis, unconfirmed_recieved_satoshis = 0, 0
    for unconfirmed_transaction in unconfirmed_transactions:
        if unconfirmed_transaction['tx_input_n'] >= 0:
            # TODO: confirm this logic
            unconfirmed_sent_satoshis += unconfirmed_transaction['value']
        else:
            unconfirmed_recieved_satoshis += unconfirmed_transaction['value']
    return {
            'btc_address': btc_address,
            'confirmed_sent_satoshis': confirmed_sent_satoshis,
            'confirmed_recieved_satoshis': confirmed_recieved_satoshis,
            'confirmed_balance_satoshis': address_details['final_balance'],
            'unconfirmed_transactions': unconfirmed_transactions,
            'confirmed_transactions': confirmed_transactions,
            'num_txns': address_details['n_tx'],
            'has_more': address_details.get('hasMore'),
            }
