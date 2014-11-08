from annoying.decorators import render_to

from blockcypher import get_address_details


@render_to('address_overview.html')
def address_overview(request, btc_address):

    # FIXME: this doesn't cover pagination and will fail silently-ish on those cases!
    address_details = get_address_details(btc_address)

    transactions = address_details['txrefs']

    # import pprint; pprint.pprint(address_details, width=1)

    # doesn't cover pagination
    sent_satoshis, recieved_satoshis = 0, 0
    for transaction in transactions:
        if transaction['tx_input_n'] >= 0:
            # TODO: confirm this logic
            sent_satoshis += transaction['value']
        else:
            recieved_satoshis += transaction['value']

    return {
            'btc_address': btc_address,
            'sent_satoshis': sent_satoshis,
            'recieved_satoshis': recieved_satoshis,
            'confirmed_balance_satoshis': address_details['final_balance'],
            'unconfirmed_balance_satoshis': address_details['balance'],
            'num_transactions': len(transactions),
            'transactions': transactions,
            'has_more': address_details.get('hasMore'),
            }
