from django import forms
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit


class BaseMetadataForm(forms.Form):
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

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
                'metadata_key',
                'metadata_value',
                Submit(
                    'submit',
                    'Upload Metadata',
                    css_class='btn btn-primary btn-lg',
                    ),
                )
        super(BaseMetadataForm, self).__init__(*args, **kwargs)
