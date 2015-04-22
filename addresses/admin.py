from django.contrib import admin

from addresses.models import AddressSubscription

from blockcypher.constants import COIN_CHOICES


# https://docs.djangoproject.com/en/1.6/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter
class CSFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Coin Symbol'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'coin'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return COIN_CHOICES

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        for coin_symbol, display_name in COIN_CHOICES:
            if self.value() == coin_symbol:
                return queryset.filter(coin_symbol=coin_symbol)


@admin.register(AddressSubscription)
class AddressSubscriptionAdmin(admin.ModelAdmin):

    def coin_symbol(self, instance):
        return self.coin_symbol
    coin_symbol.allow_tags = True

    list_display = (
            'id',
            'created_at',
            'unsubscribed_at',
            'coin_symbol',
            'b58_address',
            'notify_on_broadcast',
            'notify_on_first_confirm',
            'notify_on_sixth_confirm',
            'notify_on_deposit',
            'notify_on_withdrawal',
            'auth_user',
            'blockcypher_id',
            )

    raw_id_fields = ('auth_user', )
    search_fields = ('b58_address', 'auth_user__email', )
    list_filter = (
            CSFilter,
            'notify_on_broadcast',
            'notify_on_first_confirm',
            'notify_on_sixth_confirm',
            'notify_on_deposit',
            'notify_on_withdrawal',
            )
