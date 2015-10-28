from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from annoying.decorators import render_to

from blockexplorer.settings import BLOCKCYPHER_API_KEY
from blockexplorer.decorators import assert_valid_coin_symbol

from metadata.forms import MetadataForm

from blockcypher import get_metadata, put_metadata

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
def add_metadata(request, coin_symbol):
    '''
    Add metadata to the blockchain with blockcypher's API key
    '''
    initial = {'coin_symbol': coin_symbol}
    form = MetadataForm(initial=initial)
    if request.method == 'POST':
        form = MetadataForm(data=request.POST)
        if form.is_valid():
            metadata_key = form.cleaned_data.get('metadata_key')
            metadata_value = form.cleaned_data.get('metadata_value')
            where_to_upload = form.cleaned_data.get('where_to_upload')
            upload_string = form.cleaned_data.get('upload_string')
            coin_symbol_to_use = form.cleaned_data.get('coin_symbol')

            put_metadata_dict = {
                    'metadata_dict': {metadata_key: metadata_value},
                    'address': None,
                    'tx_hash': None,
                    'block_hash': None,
                    'api_key': BLOCKCYPHER_API_KEY,
                    'private': False,
                    'coin_symbol': coin_symbol_to_use,
                    }
            if where_to_upload == 'address':
                put_metadata_dict['address'] = upload_string
                redir_url = reverse(
                        'address_overview',
                        kwargs={
                            'coin_symbol': coin_symbol_to_use,
                            'address': upload_string,
                            },
                        )
            elif where_to_upload == 'transaction':
                put_metadata_dict['tx_hash'] = upload_string
                redir_url = reverse(
                        'transaction_overview',
                        kwargs={
                            'coin_symbol': coin_symbol_to_use,
                            'tx_hash': upload_string,
                            },
                        )
            elif where_to_upload == 'block':
                put_metadata_dict['block_hash'] = upload_string
                redir_url = reverse(
                        'block_overview',
                        kwargs={
                            'coin_symbol': coin_symbol_to_use,
                            'block_representation': upload_string,
                            },
                        )
            else:
                raise Exception('Logic Fail: This Should be Impossible')

            results = put_metadata(**put_metadata_dict)
            # import pprint; pprint.pprint(results, width=1)

            if results is True:
                msg = _('<pre>%(key)s</pre>-><pre>%(value)s</pre> succesfully uploaded to %(upload_string)s (<a href="#metadata">scroll down</a>)' % {
                    'key': metadata_key,
                    'value': metadata_value,
                    'upload_string': upload_string,
                    })
                messages.success(request, msg, extra_tags='safe')
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
        upload_string = request.GET.get('s')
        us_type = request.GET.get('t')
        if key:
            initial['metadata_key'] = key
        if value:
            initial['metadata_value'] = value
        if upload_string:
            initial['upload_string'] = upload_string
        if us_type:
            initial['where_to_upload'] = us_type
        if any([key, value, upload_string, us_type]):
            form = MetadataForm(initial=initial)
    return {
            'coin_symbol': coin_symbol,
            'form': form,
            'is_input_page': True,
            }


def metadata_forwarding(request):
    redir_url = reverse('add_metadata', kwargs={'coin_symbol': 'btc'})
    return HttpResponseRedirect(redir_url)
