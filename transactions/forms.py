from django import forms
from django.utils.translation import ugettext_lazy as _

from blockcypher.constants import COIN_CHOICES

import json


class PushTXForm(forms.Form):
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
        tx_hex = self.cleaned_data['tx_hex'].strip()
        try:
            tx_hex_dict = json.loads(tx_hex)
            if 'tx' not in tx_hex_dict:
                err_msg = _('Must be of the format {"tx": "12A45F67..."}')
                raise forms.ValidationError(err_msg)
            if len(tx_hex_dict['tx']) % 2 == 1:
                err_msg = _('Please enter a valid transaction hex')
                raise forms.ValidationError(err_msg)
            return json.dumps(tx_hex_dict['tx'])
        except ValueError:
            err_msg = _('Please enter valid JSON')
            raise forms.ValidationError(err_msg)
