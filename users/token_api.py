import requests
import json

from tokens.settings import BLOCKCYPHER_API_KEY


def register_new_token(email, new_token, first=None, last=None):
    assert new_token and email

    post_params = {
        "first": "MichaelFlaxman",
        "last": "TestingOkToToss",
        "email": "mflaxman+test@gmail.com",
        "token": new_token,
        }

    url = 'https://api.blockcypher.com/v1/tokens'

    get_params = {'token': BLOCKCYPHER_API_KEY}

    r = requests.post(url, data=json.dumps(post_params), params=get_params,
            verify=True, timeout=20)

    assert 'error' not in json.loads(r.text)

    return new_token
