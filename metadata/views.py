from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.translation import ugettext_lazy as _
from annoying.decorators import render_to

from blockexplorer.settings import BLOCKCYPHER_API_KEY
from blockexplorer.decorators import assert_valid_coin_symbol

from metadata.forms import BaseMetadataForm

from blockcypher.api import get_metadata, put_metadata, get_latest_block_hash, get_block_overview
from blockcypher.utils import is_valid_address_for_coinsymbol, is_valid_hash
from blockcypher.constants import COIN_SYMBOL_MAPPINGS

from random import choice

import json


@assert_valid_coin_symbol
def poll_metadata(request, coin_symbol, identifier_type, identifier):
    if identifier_type == 'addr':
        metadata = get_metadata(
                address=identifier,
                api_key=BLOCKCYPHER_API_KEY,
                private=True,
                coin_symbol=coin_symbol,
                )
    elif identifier_type == 'tx':
        metadata = get_metadata(
                tx_hash=identifier,
                api_key=BLOCKCYPHER_API_KEY,
                private=True,
                coin_symbol=coin_symbol,
                )
    elif identifier_type == 'block':
        metadata = get_metadata(
                block_hash=identifier,
                api_key=BLOCKCYPHER_API_KEY,
                private=True,
                coin_symbol=coin_symbol,
                )
    else:
        # shouldn't be possible
        raise(Http404)

    json_response = json.dumps(
            {'metadata': metadata},
            cls=DjangoJSONEncoder,
            sort_keys=True,
            )

    return HttpResponse(json_response, content_type='application/json')


@render_to('add_metadata.html')
def add_metadata_to_tx(request, coin_symbol, tx_hash):
    if not is_valid_hash(tx_hash):
        return Http404

    initial = {}
    form = BaseMetadataForm(initial=initial)
    if request.method == 'POST':
        form = BaseMetadataForm(data=request.POST)
        if form.is_valid():
            metadata_key = form.cleaned_data.get('metadata_key')
            metadata_value = form.cleaned_data.get('metadata_value')

            results = put_metadata(
                    metadata_dict={metadata_key: metadata_value},
                    tx_hash=tx_hash,
                    coin_symbol=coin_symbol,
                    api_key=BLOCKCYPHER_API_KEY,
                    private=False,
                    )

            # import pprint; pprint.pprint(results, width=1)

            if results is True:
                msg = _('<pre>%(key)s</pre>-><pre>%(value)s</pre> succesfully uploaded to %(upload_string)s (<a href="#metadata">scroll down</a>)' % {
                    'key': metadata_key,
                    'value': metadata_value,
                    'upload_string': tx_hash,
                    })
                messages.success(request, msg, extra_tags='safe')
                redir_url = reverse(
                    'transaction_overview',
                    kwargs={
                        'coin_symbol': coin_symbol,
                        'tx_hash': tx_hash,
                        },
                    )
                return HttpResponseRedirect(redir_url)
            elif 'error' in results:
                messages.warning(request, results.get('error'))
            elif 'errors' in results:
                for error in results.get('errors'):
                    messages.warning(request, error)

    elif request.method == 'GET':
        # Preseed tx hex if passed through GET string
        key = request.GET.get('k')
        value = request.GET.get('v')
        if key:
            initial['metadata_key'] = key
        if value:
            initial['metadata_value'] = value
        if key or value:
            form = BaseMetadataForm(initial=initial)
    return {
            'form': form,
            'is_input_page': True,
            'coin_symbol': coin_symbol,
            'tx_hash': tx_hash,
            }


@render_to('add_metadata.html')
def add_metadata_to_block(request, coin_symbol, block_hash):
    if not is_valid_hash(block_hash):
        return Http404

    initial = {}
    form = BaseMetadataForm(initial=initial)
    if request.method == 'POST':
        form = BaseMetadataForm(data=request.POST)
        if form.is_valid():
            metadata_key = form.cleaned_data.get('metadata_key')
            metadata_value = form.cleaned_data.get('metadata_value')

            results = put_metadata(
                    metadata_dict={metadata_key: metadata_value},
                    block_hash=block_hash,
                    coin_symbol=coin_symbol,
                    api_key=BLOCKCYPHER_API_KEY,
                    private=False,
                    )

            # import pprint; pprint.pprint(results, width=1)

            if results is True:
                msg = _('<pre>%(key)s</pre>-><pre>%(value)s</pre> succesfully uploaded to %(upload_string)s (<a href="#metadata">scroll down</a>)' % {
                    'key': metadata_key,
                    'value': metadata_value,
                    'upload_string': block_hash,
                    })
                messages.success(request, msg, extra_tags='safe')
                redir_url = reverse(
                    'block_overview',
                    kwargs={
                        'coin_symbol': coin_symbol,
                        'block_representation': block_hash,
                        },
                    )
                return HttpResponseRedirect(redir_url)
            elif 'error' in results:
                messages.warning(request, results.get('error'))
            elif 'errors' in results:
                for error in results.get('errors'):
                    messages.warning(request, error)

    elif request.method == 'GET':
        # Preseed tx hex if passed through GET string
        key = request.GET.get('k')
        value = request.GET.get('v')
        if key:
            initial['metadata_key'] = key
        if value:
            initial['metadata_value'] = value
        if key or value:
            form = BaseMetadataForm(initial=initial)
    return {
            'form': form,
            'is_input_page': True,
            'coin_symbol': coin_symbol,
            'block_hash': block_hash,
            }


@render_to('add_metadata.html')
def add_metadata_to_address(request, coin_symbol, address):
    if not is_valid_address_for_coinsymbol(address, coin_symbol):
        return Http404

    initial = {}
    form = BaseMetadataForm(initial=initial)
    if request.method == 'POST':
        form = BaseMetadataForm(data=request.POST)
        if form.is_valid():
            metadata_key = form.cleaned_data.get('metadata_key')
            metadata_value = form.cleaned_data.get('metadata_value')

            results = put_metadata(
                    metadata_dict={metadata_key: metadata_value},
                    address=address,
                    coin_symbol=coin_symbol,
                    api_key=BLOCKCYPHER_API_KEY,
                    private=False,
                    )

            # import pprint; pprint.pprint(results, width=1)

            if results is True:
                msg = _('<pre>%(key)s</pre>-><pre>%(value)s</pre> succesfully uploaded to %(upload_string)s (<a href="#metadata">scroll down</a>)' % {
                    'key': metadata_key,
                    'value': metadata_value,
                    'upload_string': address,
                    })
                messages.success(request, msg, extra_tags='safe')
                redir_url = reverse(
                    'address_overview',
                    kwargs={
                        'coin_symbol': coin_symbol,
                        'address': address,
                        },
                    )
                return HttpResponseRedirect(redir_url)
            elif 'error' in results:
                messages.warning(request, results.get('error'))
            elif 'errors' in results:
                for error in results.get('errors'):
                    messages.warning(request, error)

    elif request.method == 'GET':
        # Preseed tx hex if passed through GET string
        key = request.GET.get('k')
        value = request.GET.get('v')
        if key:
            initial['metadata_key'] = key
        if value:
            initial['metadata_value'] = value
        if key or value:
            form = BaseMetadataForm(initial=initial)
    return {
            'form': form,
            'is_input_page': True,
            'coin_symbol': coin_symbol,
            'address': address,
            }


def add_metadata(request, coin_symbol):
    block_hash = get_latest_block_hash(coin_symbol)

    block_overview = get_block_overview(
            block_representation=block_hash,
            coin_symbol=coin_symbol,
            txn_limit=500,
            api_key=BLOCKCYPHER_API_KEY,
            )

    random_tx_hash = choice(block_overview['txids'])

    redir_url = reverse(
            'add_metadata_to_tx',
            kwargs={'coin_symbol': coin_symbol, 'tx_hash': random_tx_hash},
            )

    msg = _('%(cs_display)s transaction %(tx_hash)s from latest block (%(latest_block_num)s) randomly selected' % {
        'cs_display': COIN_SYMBOL_MAPPINGS[coin_symbol]['currency_abbrev'],
        'tx_hash': random_tx_hash,
        'latest_block_num': intcomma(block_overview['height']),
        })

    messages.success(request, msg, extra_tags='safe')
    return HttpResponseRedirect(redir_url)


def metadata_forwarding(request):
    redir_url = reverse('add_metadata', kwargs={'coin_symbol': 'btc'})
    return HttpResponseRedirect(redir_url)
