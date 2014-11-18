from django.http import HttpResponseRedirect


class SSLMiddleware(object):
    # http://stackoverflow.com/a/9207726/1754586

    def process_request(self, request):
        if not any([request.is_secure(), request.META.get("HTTP_X_FORWARDED_PROTO", "") == 'https']):
            url = request.build_absolute_uri(request.get_full_path())
            secure_url = url.replace("http://", "https://")
            return HttpResponseRedirect(secure_url)
