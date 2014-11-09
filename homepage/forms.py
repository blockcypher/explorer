from django import forms
from django.utils.translation import ugettext_lazy as _

from bitcoins.address import is_valid_btc_address
from bitcoins.transaction import is_valid_tx_hash

from blockcypher import COIN_CHOICES


class SearchForm(forms.Form):
    search_string = forms.CharField(
        label=_('What to Search For'),
        help_text=_('Enter an address or transaction hash'),
        required=True,
        min_length=2,
        max_length=128,
        widget=forms.TextInput(attrs={'autofocus': ''}),
    )

    coin_symbol = forms.ChoiceField(
        label=_('Blockchain to Search'),
        required=True,
        choices=COIN_CHOICES,
    )

    def clean_search_string(self):
        search_string = self.cleaned_data['search_string'].strip()

        if is_valid_tx_hash(search_string) or is_valid_btc_address(search_string):
            return search_string
        else:
            err_msg = _('Not a valid bitcoin address or transaction hash')
            raise forms.ValidationError(err_msg)
