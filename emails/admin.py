from django.contrib import admin

from emails.models import SentEmail


class SentEmailAdmin(admin.ModelAdmin):
    list_display = (
            'id',
            'sent_at',
            'from_email',
            'from_name',
            'to_email',
            'to_name',
            'body_template',
            'subject',
            'auth_user',
            'address_subscription',
            'transaction_event',
            'address_forwarding',
            )
    list_filter = ('body_template', )
    raw_id_fields = ('auth_user', 'address_subscription', 'transaction_event', 'address_forwarding', )

    class Meta:
        model = SentEmail
admin.site.register(SentEmail, SentEmailAdmin)
