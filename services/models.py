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

