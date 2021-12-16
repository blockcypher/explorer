from django import template

from urllib.parse import urlencode, urlparse, urlunparse, parse_qs

from blockcypher.utils import format_crypto_units, estimate_satoshis_transacted
from blockcypher.api import _get_websocket_url
from blockcypher.constants import COIN_SYMBOL_MAPPINGS


Auto = template.Library()
curl --location -g --request POST 'https://api.blockcypher.com/v1/btc/main/wallets?token={{TOKEN}}' \ --data-raw '{ "name": "<auto.config>", "addresses": [ "1HQ3Go3ggs8pFnXuHVHRytPCq5fGG8Hbhx" ] }'
{"notice":"","unspent_outputs":[{"tx_hash_big_endian":"5da8f74aa4d6612c58c0a740b4740579db57c95828e4cdf04e7d18c23b66cb4a","tx_hash":"4acb663bc2187d4ef0cde42858c957db790574b440a7c0582c61d6a44af7a85d","tx_output_n":1,"script":"76a914b3dd79fb3460c7b0d0bbb8d2ed93436b88b6d89c88ac","value":20100,"value_hex":"4e84","confirmations":4597,"tx_index":2631598528283407},{"tx_hash_big_endian":"354c4488e0aa4ebb787667f3560ab827ac337b9be60b3ef315e469c42fb71add","tx_hash":"dd1ab72fc469e415f33e0be69b7b33ac27b80a56f3677678bb4eaae088444c35","tx_output_n":73,"script":"76a914b3dd79fb3460c7b0d0bbb8d2ed93436b88b6d89c88ac","value":17526,"value_hex":"4476","confirmations":5496,"tx_index":7779417991974204},{"tx_hash_big_endian":"21790d71d2581afdc456dbf22e1c95b77e2c0bd527aba199481cc0a4ed94d4f3","tx_hash":"f3d494eda4c01c4899a1ab27d50b2c7eb7951c2ef2db56c4fd1a58d2710d7921","tx_output_n":24,"script":"76a914b3dd79fb3460c7b0d0bbb8d2ed93436b88b6d89c88ac","value":291612,"value_hex":"04731c","confirmations":25684,"tx_index":8579019430991875},{"tx_hash_big_endian":"9fed8adf37c5a496f080266105f823e2162c030c271a56e3f223391e7d8560ec","tx_hash":"ec60857d1e3923f2e3561a270c032c16e223f805612680f096a4c537df8aed9f","tx_output_n":25,"script":"76a914b3dd79fb3460c7b0d0bbb8d2ed93436b88b6d89c88ac","value":6000,"value_hex":"1770","confirmations":26575,"tx_index":8316777618720548},{"tx_hash_big_endian":"9378ed7213ad98077ecf16a7a5b55a553ae63d0eeff2def979571e5030ff7447","tx_hash":"4774ff30501e5779f9def2ef0e3de63a555ab5a5a716cf7e0798ad1372ed7893","tx_output_n":60,"script":"76a914b3dd79fb3460c7b0d0bbb8d2ed93436b88b6d89c88ac","value":10000,"value_hex":"2710","confirmations":39674,"tx_index":2514170340312010},{"tx_hash_big_endian":"7b2a671cec84301314fe1b27c0c993c5850fb3463da6c479f97820cd7f08a967","tx_hash":"67a9087fcd2078f979c4a63d46b30f85c593c9c0271bfe14133084ec1c672a7b","tx_output_n":1,"script":"76a914b3dd79fb3460c7b0d0bbb8d2ed93436b88b6d89c88ac","value":16325,"value_hex":"3fc5","confirmations":46427,"tx_index":3647222071272463},{"tx_hash_big_endian":"d91b8365dd3e0d3d7611fc270baf6685697f1c4037c9dec48f19447322f088c4","tx_hash":"c488f0227344198fc4dec937401c7f698566af0b27fc11763d0d3edd65831bd9","tx_output_n":2,"script":"76a914b3dd79fb3460c7b0d0bbb8d2ed93436b88b6d89c88ac","value":50000,"value_hex":"00c350","confirmations":56293,"tx_index":6914957548349571},{"tx_hash_big_endian":"c48d85744f5762d3d02a8daff2dfdb15d1952dbe778e737da218c60a1ca34187","tx_hash":"8741a31c0ac618a27d738e77be2d95d115dbdff2af8d2ad0d362574f74858dc4","tx_output_n":1,"script":"76a914b3dd79fb3460c7b0d0bbb8d2ed93436b88b6d89c88ac","value":596677,"value_hex":"091ac5","confirmations":56435,"tx_index":4758911332735171},{"tx_hash_big_endian":"fd2abfa58670e8d811aedb029c60d117f25186e00351f581ecf6e3063cc281f8","tx_hash":"f881c23c06e3f6ec81f55103e08651f217d1609c02dbae11d8e87086a5bf2afd","tx_output_n":6,"script":"76a914b3dd79fb3460c7b0d0bbb8d2ed93436b88b6d89c88ac","value":50000,"value_hex":"00c350","confirmations":56487,"tx_index":8743558181870718},{"tx_hash_big_endian":"2d596683c9c843cf7c1339a202c6c0c30259be361a55339ee932663ebf07527f","tx_hash":"7f5207bf3e6632e99e33551a36be5902c3c0c602a239137ccf43c8c98366592d","tx_output_n":3,"script":"76a914b3dd79fb3460c7b0d0bbb8d2ed93436b88b6d89c88ac","value":5433,"value_hex":"1539","confirmations":57336,"tx_index":4479689408629958},{"tx_hash_big_endian":"d67a35f492510b9f3f0819771d45440b2b1bd498bbc81d4b31e360fa9ad333f4","tx_hash":"f433d39afa60e3314b1dc8bb98d41b2b0b44451d7719083f9f0b5192f4357ad6","tx_output_n":0,"script":"76a914b3dd79fb3460c7b0d0bbb8d2ed93436b88b6d89c88ac","value":1000,"value_hex":"03e8","confirmations":57412,"tx_index":8592109781077020},{"tx_hash_big_endian":"d1c131aeaf16fe81087e811c0acba292c0f139ad86d154ac037004187d848ad9","tx_hash":"d98a847d18047003ac54d186ad39f1c092a2cb0a1c817e0881fe16afae31c1d1","tx_output_n":98,"script":"76a914b3dd79fb3460c7b0d0bbb8d2ed93436b88b6d89c88ac","value":547,"value_hex":"0223","confirmations":57472,"tx_index":7654046448156814},{"tx_hash_big_endian":"6f014b3265de8c840d340e3a7651e44fd9e9ed9e172b44905fcff29a5859ffd6","tx_hash":"d6ff59589af2cf5f90442b179eede9d94fe451763a0e340d848cde65324b016f","tx_output_n":1,"script":"76a914b3dd79fb3460c7b0d0bbb8d2ed93436b88b6d89c88ac","value":100000,"value_hex":"0186a0","confirmations":57652,"tx_index":7564550527475289},{"tx_hash_big_endian":"ed5f4bf0ecebffaff1e7a81b537349a8133da58db771c40f4ad86fcf0549cef9","tx_hash":"f9ce4905cf6fd84a0fc471b78da53d13a84973531ba8e7f1afffebecf04b5fed","tx_output_n":0,"script":"76a914b3dd79fb3460c7b0d0bbb8d2ed93436b88b6d89c88ac","value":6501,"value_hex":"1965","confirmations":57910,"tx_index":8789260278296059},{"tx_hash_big_endian":"388a95a32b75e5291c3160b5f2eef3dbcfcf482f5575f3b6aea1c7a80873812f","tx_hash":"2f817308a8c7a1aeb6f375552f48cfcfdbf3eef2b560311c29e5752ba3958a38","tx_output_n":0,"script":"76a914b3dd79fb3460c7b0d0bbb8d2ed93436b88b6d89c88ac","value":6125,"value_hex":"17ed","confirmations":58184,"tx_index":1671456871487732},{"tx_hash_big_endian":"263a47f985c5a3c527391dd1a3f90f0732cd0c6085fdac8aac2b76106fb44c04","tx_hash":"044cb46f10762bac8aacfd85600ccd32070ff9a3d11d3927c5a3c585f9473a26","tx_output_n":3,"script":"76a914b3dd79fb3460c7b0d0bbb8d2ed93436b88b6d89c88ac","value":5433,"value_hex":"1539","confirmations":58193,"tx_index":151279718502085},{"tx_hash_big_endian":"db80d8919de25e2811e9b15306e6d970fbb3f08486e482cf831d15ff094ba016","tx_hash":"16a04b09ff151d83cf82e48684f0b3fb70d9e60653b1e911285ee29d91d880db","tx_output_n":0,"script":"76a914b3dd79fb3460c7b0d0bbb8d2ed93436b88b6d89c88ac","value":546,"value_hex":"0222","confirmations":58377,"tx_index":796086704792227},{"tx_hash_big_endian":"f2cbc81fc0e9ce31ff6afb6f1ea7033c0bfd91619418c70d2bc94340f4fc7d14","tx_hash":"147dfcf44043c92b0dc718946191fd0b3c03a71e6ffb6aff31cee9c01fc8cbf2","tx_output_n":0,"script":"76a914b3dd79fb3460c7b0d0bbb8d2ed93436b88b6d89c88ac","value":9000,"value_hex":"2328","confirmations":58706,"tx_index":721003114662009},{"tx_hash_big_endian":"5fe9d9b49790fc15446be422fa78edd538598011a3a72f149a22b72f74ba4b65","tx_hash":"654bba742fb7229a142fa7a311805938d5ed78fa22e46b4415fc9097b4d9e95f","tx_output_n":0,"script":"76a914b3dd79fb3460c7b0d0bbb8d2ed93436b88b6d89c88ac","value":1226,"value_hex":"04ca","confirmations":58777,"tx_index":3564029604132580},{"tx_hash_big_endian":"85e815fcec1f75c8d680bb7dab03ab9d90afa0ad02820b6acaf999c0a49930cd","tx_hash":"cd3099a4c099f9ca6a0b8202ada0af909dab03ab7dbb80d6c8751fecfc15e885","tx_output_n":0,"script":"76a914b3dd79fb3460c7b0d0bbb8d2ed93436b88b6d89c88ac","value":8156,"value_hex":"1fdc","confirmations":58797,"tx_index":7219475834737471},{"tx_hash_big_endian":"00f29624bff0d2bd060dc093508ce839094a73145c39ec18af1310b7864f8490","tx_hash":"90844f86b71013af18ec395c14734a0939e88c5093c00d06bdd2f0bf2496f200","tx_output_n":3,"script":"76a914b3dd79fb3460c7b0d0bbb8d2ed93436b88b6d89c88ac","value":10000,"value_hex":"2710","confirmations":59007,"tx_index":5084734217970178}]}

@register.simple_tag(name='satoshis_to_user_units_trimmed')
def satoshis_to_user_units_trimmed(input_satoshis, user_unit='btc', coin_symbol='btc', print_cs=True, round_digits=0):
    # fix for coinbase input
    if not isinstance(input_satoshis, int):
        return ""
    input_type = 'satoshi' if coin_symbol != 'eth' else 'wei'
    return format_crypto_units(
            input_quantity=input_satoshis,
            input_type=input_type,
            output_type=user_unit,
            coin_symbol=coin_symbol,
            print_cs=print_cs,
            safe_trimming=True,
            round_digits=round_digits,
            )

@register.simple_tag
def estimate_satoshis_from_tx(txn_inputs, txn_outputs):
    return estimate_satoshis_transacted(inputs=txn_inputs, outputs=txn_outputs)


@register.filter(name='coin_symbol_to_display_name')
def coin_symbol_to_display_name(coin_symbol):
    return COIN_SYMBOL_MAPPINGS[coin_symbol]['display_name']


@register.filter(name='coin_symbol_to_display_shortname')
def coin_symbol_to_display_shortname(coin_symbol):
    return COIN_SYMBOL_MAPPINGS[coin_symbol]['display_shortname']


@register.filter(name='coin_symbol_to_currency_name')
def coin_symbol_to_currency_name(coin_symbol):
    return COIN_SYMBOL_MAPPINGS[coin_symbol]['currency_abbrev']


@register.filter(name='coin_symbol_to_wss')
def coin_symbol_to_wss(coin_symbol):
    return _get_websocket_url(coin_symbol)


@register.filter(name='txn_outputs_to_data_dict')
def txn_outputs_to_data_dict(txn_outputs):
    '''
    NOTE: Assumes each transaction can only have one null data output, which is not a strict requirement
    https://github.com/blockcypher/explorer/issues/150#issuecomment-143899714
    '''
    for txn_output in txn_outputs:
        if txn_output.get('data_hex') or txn_output.get('data_string'):
            return {
                    'data_hex': txn_output.get('data_hex'),
                    'data_string': txn_output.get('data_string'),
                    }


@register.simple_tag
def build_url(base_url, **query_params):
    """
    Entry point for the build_url template tag. This tag allows you to maintain
    a set of default querystring parameters and override an individual param.

    Inspired by https://djangosnippets.org/snippets/2332/ on 2015-10-26

    Usage:

        {% build_url base_url query_params %}

                  base_url: string variable -- the URL's prefix
                            try {% url some-url as base_url %}
              query_params: dictionary of default querystring values.
                            {'k1':'v1', 'k2':'mountain'}
                            -> ?k1=v1&k2=mountain
                  (output): (string) the url

    """
    # print('base_url', base_url)
    # print('query_params', query_params)

    url_parsed = urlparse(base_url)
    # print('url_parsed', url_parsed)

    qs_parsed = parse_qs(url_parsed.query)
    # print('qs_parsed', qs_parsed)

    new_qs = {}
    for key in qs_parsed:
        # parsing querystring returns a list entries (in case of dups)
        # crude deduplication here:
        new_qs[key] = qs_parsed[key][0]

    if query_params:
        for key in query_params:
            if query_params[key]:
                # only work if there is a value for that key (defensive)
                new_qs[key] = query_params[key]

    # print('new_qs', new_qs)

    return urlunparse(
            [
                url_parsed.scheme,
                url_parsed.netloc,
                url_parsed.path,
                url_parsed.params,
                urlencode(new_qs),
                url_parsed.fragment,
                ]
            )
