from django import forms
from django.utils.translation import ugettext_lazy as _

from blockcypher.constants import COIN_CHOICES


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
