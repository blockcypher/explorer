import re
import random

from blockexplorer.settings import BASE_URL


def get_max_pages(num_items, items_per_page):
    if num_items < items_per_page:
        return 1
    elif num_items % items_per_page == 0:
        return num_items // items_per_page
    else:
        return num_items // items_per_page + 1


def get_client_ip(request):
    """
    Get IP from a request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    return request.META.get('HTTP_USER_AGENT')


def is_good_status_code(status_code):
    return str(status_code).startswith('2')


def assert_good_status_code(status_code):
    err_msg = 'Expected status code 2XX but got %s' % status_code
    assert is_good_status_code(status_code), err_msg


def simple_csprng(num_chars=32, eligible_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789'):

    """
    Generate a random password using the characters in `chars` and with a length of `num_chars`.

    http://stackoverflow.com/a/2257449

    Cryptographically secure but may not work on all OSs.
    Shouldn't cause blocking but it's possible.
    """
    return ''.join(random.SystemRandom().choice(eligible_chars) for x in range(num_chars))


def simple_pw_generator(num_chars=10, eligible_chars='abcdefghjkmnpqrstuvwxyz23456789'):
    """
    Generate a random password using the characters in `chars` and with a
    length of `size`.

    http://stackoverflow.com/a/2257449
    """
    return ''.join(random.choice(eligible_chars) for x in range(num_chars))


def uri_to_url(uri, base_url=BASE_URL):
    """
    Take a URI and map it a URL:
    /foo -> http://coinsafe.com/foo
    """
    if not uri:
        return base_url
    if uri.startswith('/'):
        return '%s%s' % (base_url, uri)
    return '%s/%s' % (base_url, uri)


def cat_email_header(name, email):
    assert '@' in email
    if name:
        return '%s <%s>' % (name, email)
    return email


def split_email_header(header):
    if '<' in header and '>' in header:
        name, email = re.findall('(.*)<(.*)>', header)[0]
    else:
        name = None
        email = header
    assert '@' in email
    return name, email
