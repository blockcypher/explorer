from django.contrib import admin

from emails.models import SentEmail

from bitmit.custom import ReadOnlyModelAdmin


class SentEmailAdmin(ReadOnlyModelAdmin):
    list_display = (
            'id',
            'sent_at',
            'from_email',
            'from_name',
            'to_email',
            'to_name',
            'body_template',
            'subject',
            'address_subscription',
            'transaction_notification',
            )
    list_filter = ('body_template', )
    raw_id_fields = ('address_subscription', 'transaction_notification', )

    class Meta:
        model = SentEmail
admin.site.register(SentEmail, SentEmailAdmin)
