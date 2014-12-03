from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from annoying.decorators import render_to
from blockexplorer.decorators import assert_valid_coin_symbol

from transactions.forms import PushTXForm

from blockexplorer.settings import BLOCKCYPHER_PUBLIC_KEY, BLOCKCYPHER_API_KEY

from blockcypher.api import get_transaction_details, get_transaction_url, pushtx

from binascii import unhexlify

import json


@assert_valid_coin_symbol
@render_to('transaction_overview.html')
def transaction_overview(request, coin_symbol, tx_hash):

    transaction_details = get_transaction_details(
            tx_hash=tx_hash,
            coin_symbol=coin_symbol,
            limit=500,
            api_key=BLOCKCYPHER_API_KEY,
            )

    # FIXME: fails silently on pagination if there are > 20 inputs or outputs

    #import pprint; pprint.pprint(transaction_details, width=1)

    if 'error' in transaction_details:
        # Corner case, such as a validly formed tx hash with no matching transaction
        msg = _('No transaction found with the hash %(tx_hash)s' % {'tx_hash': tx_hash})
        messages.warning(request, msg)
        return HttpResponseRedirect(reverse('home'))

    confidence = transaction_details.get('confidence')
    if confidence:
        confidence_pct = confidence * 100
    else:
        confidence_pct = None

    received_at = transaction_details['received']
    confirmed_at = transaction_details.get('confirmed')
    inputs = transaction_details['inputs']
    outputs = transaction_details['outputs']
    total_satoshis = transaction_details['total']
    fee_in_satoshis = transaction_details['fees']

    if confirmed_at:
        if received_at >= confirmed_at:
            diff = received_at - confirmed_at
        else:
            diff = confirmed_at - received_at

        if diff.seconds < 60*20:
            time_to_use = received_at
        else:
            time_to_use = confirmed_at
    else:
        time_to_use = received_at

    if inputs[0]['addresses']:
        is_coinbase_tx = False
        total_satoshis_coinbase, fee_in_satoshis_coinbase = None, None
        coinbase_msg = None
    else:
        is_coinbase_tx = True
        total_satoshis_coinbase = inputs[0]['output_value']
        fee_in_satoshis_coinbase = total_satoshis - total_satoshis_coinbase
        coinbase_msg = str(unhexlify(inputs[0]['script']))

    api_url = get_transaction_url(tx_hash=tx_hash, coin_symbol=coin_symbol)

    return {
            'coin_symbol': coin_symbol,
            'tx_hash': tx_hash,
            'api_url': api_url,
            'is_coinbase_tx': is_coinbase_tx,
            'coinbase_msg': coinbase_msg,
            'double_of_tx': transaction_details.get('double_of'),
            'received_at': received_at,
            'confirmed_at': confirmed_at,
            'time_to_use': time_to_use,
            'total_satoshis': total_satoshis,
            'total_satoshis_coinbase': total_satoshis_coinbase,
            'fee_in_satoshis': fee_in_satoshis,
            'fee_in_satoshis_coinbase': fee_in_satoshis_coinbase,
            'block_height': transaction_details['block_height'],
            'block_hash': transaction_details.get('block_hash'),
            'inputs': inputs,
            'outputs': outputs,
            'num_confirmations': transaction_details['confirmations'],
            'relayed_by': transaction_details['relayed_by'],
            'num_inputs': transaction_details['vin_sz'],
            'num_outputs': transaction_details['vout_sz'],
            'confidence_pct': confidence_pct,
            'preference': transaction_details.get('preference'),
            'receive_cnt': transaction_details.get('receive_count'),
            'BLOCKCYPHER_PUBLIC_KEY': BLOCKCYPHER_PUBLIC_KEY,
            }


@assert_valid_coin_symbol
def poll_confidence(request, coin_symbol, tx_hash):
    transaction_details = get_transaction_details(
            tx_hash=tx_hash,
            coin_symbol=coin_symbol,
            limit=1,
            api_key=BLOCKCYPHER_API_KEY,
            )

    confidence = transaction_details.get('confidence')
    if confidence:
        confidence_pct = min(round(confidence * 100, 2), 99.99)
    else:
        confidence_pct = None

    json_dict = {
            'confidence': confidence,
            'confidence_pct': confidence_pct,
            'double_spend_detected': transaction_details['double_spend'],
            'receive_cnt': transaction_details.get('receive_count'),
            }

    json_response = json.dumps(json_dict, cls=DjangoJSONEncoder)

    return HttpResponse(json_response, content_type='application/json')


@render_to('pushtx.html')
def push_tx(request, coin_symbol):
    form = PushTXForm(initial={'coin_symbol': coin_symbol})
    if request.method == 'POST':
        form = PushTXForm(data=request.POST)
        if form.is_valid():
            # broadcast the transaction
            tx_hex = form.cleaned_data['tx_hex']
            coin_symbol_to_use = form.cleaned_data['coin_symbol']

            result = pushtx(tx_hex=tx_hex, coin_symbol=coin_symbol_to_use, api_key=BLOCKCYPHER_API_KEY)
            #import pprint; pprint.pprint(result, width=1)

            if result.get('errors'):
                err_msg = _('Transaction not broadcast for the following errors')
                messages.error(request, err_msg)
                for error in result['errors']:
                    messages.info(request, error['error'])
            else:
                success_msg = _('Transaction Succesfully Broadcst')
                messages.success(request, success_msg)
                url = reverse('transaction_overview', kwargs={
                    'coin_symbol': coin_symbol_to_use,
                    'tx_hash': result['tx']['hash'],
                    })
                return HttpResponseRedirect(url)

    return {
            'coin_symbol': coin_symbol,
            'form': form,
            }
