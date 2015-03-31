from django.contrib import admin

from transactions.models import OnChainTransaction


@admin.register(OnChainTransaction)
class OnChainTransactionAdmin(admin.ModelAdmin):
    list_display = (
            'id',
            'created_at',
            'tx_hash',
            'address_subscription',
            'num_confs',
            'double_spend',
            )
    raw_id_fields = ('address_subscription', )
    search_fields = ('tx_hash', 'address_subscription', )

    class Meta:
        model = OnChainTransaction
