from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from annoying.decorators import render_to

from homepage.forms import SearchForm

from bitcoins.transaction import is_valid_tx_hash


@render_to('home.html')
def home(request):
    form = SearchForm()
    if request.method == 'POST':
        form = SearchForm(data=request.POST)
        if form.is_valid():
            search_string = form.cleaned_data['search_string']
            if is_valid_tx_hash(search_string):
                return HttpResponseRedirect(reverse('transaction_overview',
                    kwargs={'tx_hash': search_string}))
            else:
                return HttpResponseRedirect(reverse('address_overview',
                    kwargs={'btc_address': search_string}))

    return {'form': form}
