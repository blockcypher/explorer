from django.http import Http404

from blockcypher.constants import COIN_SYMBOL_MAPPINGS


class assert_valid_coin_symbol(object):

    def __init__(self, func):
        self.func = func

    def __call__(self, request, *args, **kwargs):
        if kwargs.get('coin_symbol') not in COIN_SYMBOL_MAPPINGS:
            raise(Http404)
        return self.func(request, *args, **kwargs)
