from annoying.decorators import render_to

from blockcypher import get_transactions_details


@render_to('transaction_overview.html')
def transaction_overview(request, tx_hash):

    transaction_details = get_transactions_details(tx_hash)

    # FIXME: fails silently on pagination if there are > 20 inputs or outputs

    # import pprint; pprint.pprint(transaction_details, width=1)

    return {
            'tx_hash': tx_hash,
            'received_at': transaction_details['received'],
            'confirmed_at': transaction_details.get('confirmed'),
            'double_spend': transaction_details['double_spend'],
            'total_satoshis': transaction_details['total'],
            'sent_satoshis': 0,
            'recieved_satoshis': 0,
            'fee_in_satoshis': transaction_details['fees'],
            'block_height': transaction_details['block_height'],
            'block_hash': transaction_details.get('block_hash'),
            'inputs': transaction_details['inputs'],
            'outputs': transaction_details['outputs'],
            'num_confirmations': transaction_details['confirmations'],
            'relayed_by': transaction_details['relayed_by'],
            'num_inputs': transaction_details['vin_sz'],
            'num_outputs': transaction_details['vout_sz'],
            }
