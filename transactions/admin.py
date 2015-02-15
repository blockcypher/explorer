from django.contrib import admin

from transactions.models import TransactionEvent


@admin.register(TransactionEvent)
class TransactionEventAdmin(admin.ModelAdmin):
    list_display = (
            'id',
            'created_at',
            'tx_hash',
            'b58_address',
            'address_subscription',
            )
    raw_id_fields = ('address_subscription', )
    search_fields = ('tx_hash', 'b58_address', )

    class Meta:
        model = TransactionEvent
