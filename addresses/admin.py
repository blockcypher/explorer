from django.contrib import admin

from addresses.models import AddressSubscription


@admin.register(AddressSubscription)
class AddressSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
            'id',
            'created_at',
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
    search_fields = ('b58_address', 'auth_user', )

    class Meta:
        model = AddressSubscription
