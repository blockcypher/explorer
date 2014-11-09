from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from annoying.decorators import render_to

from homepage.forms import SearchForm

from bitcoins.utils import is_valid_tx_hash, is_valid_block_representation


@render_to('home.html')
def home(request):
    form = SearchForm(initial={
        'search_string': '16Fg2yjwrbtC6fZp61EV9mNVKmwCzGasw5',
        'coin_symbol': 'btc',
        })
    if request.method == 'POST':
        form = SearchForm(data=request.POST)
        if form.is_valid():
            search_string = form.cleaned_data['search_string']
            coin_symbol = form.cleaned_data['coin_symbol']
            kwargs = {'coin_symbol': coin_symbol}
            if is_valid_block_representation(search_string):
                kwargs['block_representation'] = search_string
                redirect_url = reverse('block_overview', kwargs=kwargs)
            elif is_valid_tx_hash(search_string):
                kwargs['tx_hash'] = search_string
                redirect_url = reverse('transaction_overview', kwargs=kwargs)
            else:
                kwargs['address'] = search_string
                redirect_url = reverse('address_overview', kwargs=kwargs)

            return HttpResponseRedirect(redirect_url)

    return {'form': form}
