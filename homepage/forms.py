from django import forms
from django.utils.translation import ugettext_lazy as _

from blockcypher.constants import COIN_CHOICES
from blockcypher.utils import is_valid_address, is_valid_hash, is_valid_block_num


class SearchForm(forms.Form):
    search_string = forms.CharField(
        required=True,
        min_length=2,
        max_length=128,
    )

    coin_symbol = forms.ChoiceField(
        required=False,
        choices=COIN_CHOICES,
    )

    def clean_search_string(self):
        search_string = self.cleaned_data['search_string'].strip().replace(',', '')

        if is_valid_hash(search_string) or is_valid_address(search_string) or is_valid_block_num(search_string):
            return search_string
        else:
            err_msg = _('Not a valid address, transaction hash, or block number')
            raise forms.ValidationError(err_msg)
