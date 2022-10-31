from django.db import models

from jsonfield import JSONField

from utils import get_client_ip, uri_to_url, is_good_status_code, get_user_agent

import json
import requests


class APICall(models.Model):
    """
    To keep track of all our external API calls and aid in debugging as well.
    """

    API_NAME_CHOICES = ()

    # Main fields
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    api_name = models.CharField(choices=API_NAME_CHOICES, max_length=3, null=False, blank=False, db_index=True)
    url_hit = models.URLField(max_length=1024, blank=False, null=False, db_index=True)
    response_code = models.PositiveSmallIntegerField(blank=False, null=False, db_index=True)
    post_params = JSONField(blank=True, null=True)
    headers = models.CharField(max_length=2048, null=True, blank=True)
    api_results = models.CharField(max_length=100000, blank=True, null=True)

    def __str__(self):
        return '%s from %s' % (self.id, self.api_name)


class WebHook(models.Model):
    """
    To keep track of all our webhooks and aid in debugging as well.
    """
    # api_name choices
    BLOCKCYPHER_ADDRESS_NOTIFICATION = 'BAN'

    API_NAME_CHOICES = (
            (BLOCKCYPHER_ADDRESS_NOTIFICATION, 'blockcypher address notification'),
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    # IP and UA of machine hitting coinsafe
    ip_address = models.GenericIPAddressField(null=False, blank=False, db_index=True)
    user_agent = models.CharField(max_length=1024, blank=True, db_index=True)
    api_name = models.CharField(choices=API_NAME_CHOICES, max_length=3, null=False, blank=False, db_index=True)
    hostname = models.CharField(max_length=512, blank=False, null=False, db_index=True)
    request_path = models.CharField(max_length=2048, blank=False, null=False, db_index=True)
    uses_https = models.BooleanField(db_index=True, default=False)
    succeeded = models.BooleanField(db_index=True, default=False)
    data_from_get = JSONField(blank=True, null=True)
    data_from_post = JSONField(blank=True, null=True)

    # optional FKs
    address_subscription = models.ForeignKey('addresses.AddressSubscription', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return '%s from %s' % (self.id, self.api_name)

    @classmethod
    def log_webhook(cls, request, api_name):
        try:
            data_from_post = json.loads(request.body.decode())
        except Exception:
            client.captureException()
            data_from_post = None
        return cls.objects.create(
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                api_name=api_name,
                hostname=request.get_host(),
                request_path=request.path,
                uses_https=request.is_secure(),
                data_from_get=request.GET,
                data_from_post=data_from_post,
                )

    def retry_webhook(self):
        " Debug method to be called at the command line only "
        url_to_hit = uri_to_url(self.request_path)
        if self.data_from_get:
            r = requests.get(url_to_hit, params=self.data_from_get)
        elif self.data_from_post:
            r = requests.post(url_to_hit, params=json.dumps(self.data_from_post))

        if is_good_status_code(r.status_code):
            return True
        else:
            return r.text
