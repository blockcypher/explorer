from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from annoying.decorators import render_to
from blockexplorer.decorators import assert_valid_coin_symbol

from transactions.forms import RawTXForm, EmbedDataForm

from blockexplorer.settings import BLOCKCYPHER_PUBLIC_KEY, BLOCKCYPHER_API_KEY

from blockcypher.api import get_transaction_details, pushtx, decodetx, get_broadcast_transactions, embed_data
from blockcypher.constants import COIN_SYMBOL_MAPPINGS

from binascii import unhexlify

import json


def scale_confidence(confidence):
    """
    Hack so that 95% confidence doesn't look like basically 100%
    """
    if confidence is None:
        return 0

    assert confidence <= 1

    confidence_scaled = confidence**10  # arbitrary fudge factor
    return confidence_scaled * 100


@assert_valid_coin_symbol
@render_to('transaction_overview.html')
def transaction_overview(request, coin_symbol, tx_hash):

    try:
        transaction_details = get_transaction_details(
                tx_hash=tx_hash,
                coin_symbol=coin_symbol,
                limit=500,
                api_key=BLOCKCYPHER_API_KEY,
                include_hex=True,
                )
    except AssertionError:
        msg = _('Invalid Transaction Hash')
        messages.warning(request, msg)
        redir_url = reverse('coin_overview', kwargs={'coin_symbol': coin_symbol})
        return HttpResponseRedirect(redir_url)

    # import pprint; pprint.pprint(transaction_details, width=1)

    if 'error' in transaction_details:
        # Corner case, such as a validly formed tx hash with no matching transaction
        msg = _('No transaction found with the hash %(tx_hash)s' % {'tx_hash': tx_hash})
        messages.warning(request, msg)
        return HttpResponseRedirect(reverse('home'))

    confidence = transaction_details.get('confidence')
    if confidence:
        confidence_pct = confidence * 100
        confidence_pct_scaled = scale_confidence(confidence)
    else:
        confidence_pct, confidence_pct_scaled = None, None

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

    if 'prev_hash' in inputs[0]:
        is_coinbase_tx = False
        total_satoshis_coinbase, fee_in_satoshis_coinbase = None, None
        coinbase_msg = None
    else:
        is_coinbase_tx = True
        total_satoshis_coinbase = inputs[0]['output_value']
        fee_in_satoshis_coinbase = total_satoshis - total_satoshis_coinbase
        coinbase_msg = str(unhexlify(inputs[0]['script']))

    api_url = 'https://api.blockcypher.com/v1/%s/%s/txs/%s?includeHex=true' % (
            COIN_SYMBOL_MAPPINGS[coin_symbol]['blockcypher_code'],
            COIN_SYMBOL_MAPPINGS[coin_symbol]['blockcypher_network'],
            tx_hash,
            )

    return {
            'coin_symbol': coin_symbol,
            'tx_hash': tx_hash,
            'api_url': api_url,
            'is_coinbase_tx': is_coinbase_tx,
            'coinbase_msg': coinbase_msg,
            'received_at': received_at,
            'confirmed_at': confirmed_at,
            'time_to_use': time_to_use,
            'total_satoshis': total_satoshis,
            'total_satoshis_coinbase': total_satoshis_coinbase,
            'fee_in_satoshis': fee_in_satoshis,
            'fee_in_satoshis_coinbase': fee_in_satoshis_coinbase,
            'inputs': inputs,
            'outputs': outputs,
            'confidence_pct': confidence_pct,
            'confidence_pct_scaled': confidence_pct_scaled,
            'transaction': transaction_details,
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
            'confidence_pct_scaled': scale_confidence(confidence),
            'double_spend_detected': transaction_details['double_spend'],
            'receive_cnt': transaction_details.get('receive_count'),
            }

    json_response = json.dumps(json_dict, cls=DjangoJSONEncoder)

    return HttpResponse(json_response, content_type='application/json')


def pushtx_forwarding(request):
    kwargs = {'coin_symbol': 'btc'}
    redir_url = reverse('push_tx', kwargs=kwargs)
    return HttpResponseRedirect(redir_url)


@render_to('pushtx.html')
def push_tx(request, coin_symbol):
    '''
    Push a raw TX to the bitcoin network
    '''
    initial = {'coin_symbol': coin_symbol}
    form = RawTXForm(initial=initial)
    if request.method == 'POST':
        form = RawTXForm(data=request.POST)
        if form.is_valid():
            # broadcast the transaction
            tx_hex = form.cleaned_data['tx_hex']
            coin_symbol_to_use = form.cleaned_data['coin_symbol']

            result = pushtx(tx_hex=tx_hex, coin_symbol=coin_symbol_to_use, api_key=BLOCKCYPHER_API_KEY)
            # import pprint; pprint.pprint(result, width=1)

            if result.get('errors'):
                for error in result.get('errors'):
                    messages.error(request, error['error'])
            elif result.get('error'):
                messages.error(request, result.get('error'))
            else:
                success_msg = _('Transaction Successfully Broadcst')
                messages.success(request, success_msg)
                url = reverse('transaction_overview', kwargs={
                    'coin_symbol': coin_symbol_to_use,
                    'tx_hash': result['tx']['hash'],
                    })
                return HttpResponseRedirect(url)
    elif request.method == 'GET':
        # Preseed tx hex if passed through GET string
        tx_hex = request.GET.get('t')
        if tx_hex:
            initial['tx_hex'] = tx_hex
            form = RawTXForm(initial=initial)

    return {
            'coin_symbol': coin_symbol,
            'form': form,
            }


@render_to('decodetx.html')
def decode_tx(request, coin_symbol):
    '''
    Decode a raw transaction
    '''
    initial = {'coin_symbol': coin_symbol}
    form = RawTXForm(initial=initial)
    tx_in_json_str = ''
    if request.method == 'POST':
        form = RawTXForm(data=request.POST)
        if form.is_valid():
            # Display the TX
            tx_hex = form.cleaned_data['tx_hex']
            coin_symbol_to_use = form.cleaned_data['coin_symbol']

            tx_in_json = decodetx(tx_hex=tx_hex, coin_symbol=coin_symbol_to_use)
            tx_in_json_str = json.dumps(tx_in_json, indent=4)
            # print(tx_in_json_str)

    elif request.method == 'GET':
        # Preseed tx hex if passed through GET string
        tx_hex = request.GET.get('t')
        if tx_hex:
            initial['tx_hex'] = tx_hex
            form = RawTXForm(initial=initial)
    return {
            'coin_symbol': coin_symbol,
            'form': form,
            'tx_in_json_str': tx_in_json_str,
            }


def decodetx_forwarding(request):
    kwargs = {'coin_symbol': 'btc'}
    redir_url = reverse('decode_tx', kwargs=kwargs)
    return HttpResponseRedirect(redir_url)


@render_to('embedtx.html')
def embed_txdata(request, coin_symbol):
    '''
    Embed data in the blockchain with blockcypher's API key
    '''
    initial = {'coin_symbol': coin_symbol}
    form = EmbedDataForm(initial=initial)
    if request.method == 'POST':
        form = EmbedDataForm(data=request.POST)
        if form.is_valid():
            data_to_embed = form.cleaned_data['data_to_embed']
            encoding_is_hex = form.cleaned_data['encoding_is_hex']
            coin_symbol_to_use = form.cleaned_data['coin_symbol']

            results = embed_data(
                    to_embed=data_to_embed,
                    api_key=BLOCKCYPHER_API_KEY,
                    data_is_hex=encoding_is_hex,
                    coin_symbol=coin_symbol_to_use,
                    )
            if 'error' in results:
                messages.warning(request, results.get('error'))
            elif 'errors' in results:
                for error in results.get('errors'):
                    messages.warning(request, error)
            else:
                # import pprint; pprint.pprint(results, width=1)
                tx_hash = results['hash']
                kwargs = {
                        'coin_symbol': coin_symbol_to_use,
                        'tx_hash': tx_hash,
                        }
                msg = _('Data succesfully embedded into TX <strong>%(tx_hash)s</strong>' % {
                    'tx_hash': tx_hash,
                    })
                messages.success(request, msg, extra_tags='safe')
                return HttpResponseRedirect(reverse('transaction_overview', kwargs=kwargs))

    elif request.method == 'GET':
        # Preseed tx hex if passed through GET string
        tx_hex = request.GET.get('d')
        encoding_is_hex = request.GET.get('e')
        if tx_hex:
            initial['data_to_embed'] = tx_hex
        if encoding_is_hex:
            initial['encoding_is_hex'] = encoding_is_hex
        if tx_hex or encoding_is_hex:
            form = RawTXForm(initial=initial)
    return {
            'coin_symbol': coin_symbol,
            'form': form,
            'is_embed_page': True,  # template hack
            }


def embed_txdata_forwarding(request):
    redir_url = reverse('embed_txdata', kwargs={'coin_symbol': 'btc'})
    return HttpResponseRedirect(redir_url)


def latest_unconfirmed_tx(request, coin_symbol):
    recent_tx_hash = get_broadcast_transactions(
            coin_symbol=coin_symbol,
            api_key=BLOCKCYPHER_API_KEY,
            limit=1)[0]['hash']
    kwargs = {
            'coin_symbol': coin_symbol,
            'tx_hash': recent_tx_hash,
            }
    return HttpResponseRedirect(reverse('transaction_overview', kwargs=kwargs))


def latest_unconfirmed_tx_forwarding(request):
    return HttpResponseRedirect(reverse('latest_unconfirmed_tx',
        kwargs={'coin_symbol': 'btc'}
        ))
