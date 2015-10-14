from django import forms
from django.utils.translation import ugettext_lazy as _

from blockcypher.constants import COIN_CHOICES
from blockcypher.utils import uses_only_hash_chars

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit


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


class EmbedDataForm(forms.Form):
    '''
    Used for both pushing and decoding
    '''

    data_to_embed = forms.CharField(
        label=_('Data to Embed'),
        required=True,
        widget=forms.Textarea(attrs={'class': 'input-lg', 'autofocus': 'autofocus'}),
        min_length=1,
        max_length=400,
    )

    encoding_is_hex = forms.BooleanField(
        label=_('Data is Hexadecimal'),
        initial=True,
        required=False,
    )

    def clean_data_to_embed(self):
        data_to_embed = self.cleaned_data['data_to_embed'].strip()
        if False:
            # FIXME
            err_msg = _('Please enter a valid transaction hex')
            raise forms.ValidationError(err_msg)
        return data_to_embed

    def clean(self):
        encoding_is_hex = self.cleaned_data.get('encoding_is_hex')
        if encoding_is_hex is None:
            return None
        data_to_embed = self.cleaned_data.get('data_to_embed')

        if encoding_is_hex:
            if not uses_only_hash_chars(data_to_embed):
                msg = _('Sorry, that string contains non-hex characters. Uncheck "Data is Hexadecimal" to instead embed the data as a string.')
                raise forms.ValidationError(msg)

        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
                'data_to_embed',
                'encoding_is_hex',
                Submit(
                    'submit',
                    'Embed Data',
                    css_class='btn btn-primary btn-lg',
                    ),
                )
        super(EmbedDataForm, self).__init__(*args, **kwargs)
