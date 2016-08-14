from django.contrib import admin

from services.models import APICall, WebHook


@admin.register(APICall)
class APICallAdmin(admin.ModelAdmin):
    list_display = (
            'id',
            'created_at',
            'api_name',
            'url_hit',
            'response_code',
            'post_params',
            'headers',
            'api_results',
            )
    list_filter = ('api_name', 'response_code', )

    class Meta:
        model = APICall


@admin.register(WebHook)
class WebHookAdmin(admin.ModelAdmin):
    list_display = (
            'id',
            'created_at',
            'succeeded',
            'ip_address',
            'user_agent',
            'api_name',
            'hostname',
            'request_path',
            'uses_https',
            'data_from_get',
            'data_from_post',
            'address_subscription',
            )
    list_filter = ('api_name', 'succeeded', 'uses_https', 'user_agent', )
    raw_id_fields = ('address_subscription', )

    class Meta:
        model = WebHook
