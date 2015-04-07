from django import forms
from django.utils.translation import ugettext_lazy as _

from blockcypher.constants import COIN_CHOICES


class RawTXForm(forms.Form):
    '''
    Used for both pushing and decoding
    '''

    tx_hex = forms.CharField(
        label=_('Transaction Hex'),
        required=True,
        widget=forms.Textarea(attrs={'class': 'input-lg', 'autofocus': 'autofocus'}),
        min_length=10,  # TODO: accurate min
    )

    coin_symbol = forms.ChoiceField(
        label=_('Network'),
        required=True,
        choices=COIN_CHOICES,
    )

    def clean_tx_hex(self):
        tx_hex = self.cleaned_data['tx_hex'].strip().upper()
        if len(tx_hex) % 2 == 1:
            err_msg = _('Please enter a valid transaction hex')
            raise forms.ValidationError(err_msg)
        return tx_hex
