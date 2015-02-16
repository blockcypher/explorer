from django.contrib import admin

from transactions.models import TransactionEvent


@admin.register(TransactionEvent)
class TransactionEventAdmin(admin.ModelAdmin):
    list_display = (
            'id',
            'created_at',
            'tx_hash',
            'address_subscription',
            'conf_num',
            'double_spend',
            )
    raw_id_fields = ('address_subscription', )
    search_fields = ('tx_hash', 'address_subscription', )

    class Meta:
        model = TransactionEvent
