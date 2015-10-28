from django import forms
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from crispy_forms.bootstrap import InlineRadios


from blockcypher.constants import COIN_CHOICES, COIN_SYMBOL_MAPPINGS
from blockcypher.utils import is_valid_address_for_coinsymbol, is_valid_hash


class MetadataForm(forms.Form):
    '''
    Used for uploading public metadata
    '''

    metadata_key = forms.CharField(
        label=_('Metadata Key'),
        required=True,
        widget=forms.TextInput(attrs={'class': 'input-lg', 'autofocus': 'autofocus'}),
        min_length=1,
        max_length=256,
        )

    metadata_value = forms.CharField(
        label=_('Metadata Value'),
        required=True,
        widget=forms.TextInput(attrs={'class': 'input-lg'}),
        min_length=1,
        max_length=512,
        )

    where_to_upload = forms.ChoiceField(
        label=_('Upload Type'),
        required=True,
        choices=(
            ('address', 'Address'),
            ('transaction', 'Transaction Hash'),
            ('block', 'Block Hash'),
            ),
        widget=forms.RadioSelect,
        initial='address',
        help_text=_('You can upload metadata to an address, transaction or block'),
        )

    upload_string = forms.CharField(
        label=_('Upload Type Value'),
        required=True,
        # TODO: adjust placeholder based on which coin-symbol is selected.
        # Also, adjust if not address is toggled
        widget=forms.TextInput(attrs={'class': 'input-lg', 'placeholder': '1AddressHere'}),
        min_length=1,
        max_length=256,
        help_text='Address, Tranasaction Hash, or Block Hash to Upload To',
        )

    coin_symbol = forms.ChoiceField(
        label=_('Network'),
        required=True,
        choices=COIN_CHOICES,
        help_text=_('Currently only the Bitcoin Mainnet and Blockcypher Testnets are supported'),
        )

    def clean(self):
        where_to_upload = self.cleaned_data.get('where_to_upload')
        upload_string = self.cleaned_data.get('upload_string')
        coin_symbol = self.cleaned_data.get('coin_symbol')
        if not where_to_upload or not upload_string:
            return self.cleaned_data
        if where_to_upload == 'address':
            if not is_valid_address_for_coinsymbol(upload_string, coin_symbol):
                cs_display = COIN_SYMBOL_MAPPINGS[coin_symbol]['display_name']
                msg = _("Sorry, that's not a valid address for %(coin_symbol)s" % {'coin_symbol': cs_display})
                raise forms.ValidationError(msg)
        elif where_to_upload == 'transaction':
            if not is_valid_hash(upload_string):
                msg = _("Sorry, that's not a valid transaction hash")
                raise forms.ValidationError(msg)
        elif where_to_upload == 'block':
            if not is_valid_hash(upload_string):
                msg = _("Sorry, that's not a valid block hash")
                raise forms.ValidationError(msg)
        else:
            raise Exception('Logic Fail: Not Possible')

        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
                'metadata_key',
                'metadata_value',
                InlineRadios('where_to_upload'),
                'upload_string',
                'coin_symbol',
                Submit(
                    'submit',
                    'Upload Metadata',
                    css_class='btn btn-primary btn-lg',
                    ),
                )
        super(MetadataForm, self).__init__(*args, **kwargs)
