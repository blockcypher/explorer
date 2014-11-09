from annoying.decorators import render_to

from blockcypher import get_block_details


@render_to('block_overview.html')
def block_overview(request, coin_symbol, block_representation):

    # TODO: this doesn't cover pagination >500 and will fail silently-ish on those cases!
    block_details = get_block_details(
            block_representation=block_representation,
            coin_symbol=coin_symbol,
            max_txns=500)

    # import pprint; pprint.pprint(block_details, width=1)

    return {
            'coin_symbol': coin_symbol,
            'block_details': block_details,
            }
