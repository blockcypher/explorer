from annoying.decorators import render_to

from blockexplorer.decorators import assert_valid_coin_symbol
from blockexplorer.settings import BLOCKCYPHER_API_KEY

from blockcypher import get_wallet_details, create_hd_wallet
from blockcypher.utils import get_blockcypher_walletname_from_mpub

from utils import get_max_pages


@assert_valid_coin_symbol
@render_to('address_overview.html')
def wallet_overview(request, coin_symbol, pubkey, subchain_indices=''):

    subchain_indices = subchain_indices.split('-')
    if subchain_indices == ['']:
        subchain_indices = []
    else:
        subchain_indices = [int(x) for x in subchain_indices]

    # TODO: confirm it's a pubkey and not a privkey

    TXNS_PER_PAGE = 100

    # 1 indexed page
    current_page = request.GET.get('page')
    if current_page:
        current_page = int(current_page)
    else:
        current_page = 1

    # transaction pagination: 0-indexed and inclusive
    tx_start_num = (current_page - 1) * TXNS_PER_PAGE
    tx_end_num = current_page * TXNS_PER_PAGE - 1

    wallet_name = get_blockcypher_walletname_from_mpub(mpub=pubkey,
            subchain_indices=subchain_indices)

    # TODO: could store in DB whether created or not
    create_hd_wallet(
            wallet_name=wallet_name,
            xpubkey=pubkey,
            api_key=BLOCKCYPHER_API_KEY,
            subchain_indices=subchain_indices,
            coin_symbol=coin_symbol,
            )

    wallet_details = get_wallet_details(
            wallet_name=wallet_name,
            coin_symbol=coin_symbol,
            txn_limit=TXNS_PER_PAGE,
            api_key=BLOCKCYPHER_API_KEY,
            )
    #import pprint; pprint.pprint(wallet_details, width=1)

    assert 'error' not in wallet_details, wallet_details

    all_transactions = wallet_details.get('unconfirmed_txrefs', []) + wallet_details.get('txrefs', [])

    # filter address details for pagination. HACK!
    all_transactions = all_transactions[tx_start_num:tx_end_num]

    return {
            'is_wallet_page': True,  # shared template
            'coin_symbol': coin_symbol,
            'pubkey': pubkey,
            'subchain_indices': subchain_indices,
            'current_page': current_page,
            'max_pages': get_max_pages(num_items=wallet_details['final_n_tx'], items_per_page=TXNS_PER_PAGE),
            'total_sent_satoshis': wallet_details['total_sent'],
            'total_received_satoshis': wallet_details['total_received'],
            'unconfirmed_balance_satoshis': wallet_details['unconfirmed_balance'],
            'confirmed_balance_satoshis': wallet_details['balance'],
            'total_balance_satoshis': wallet_details['final_balance'],
            'all_transactions': all_transactions,
            'num_confirmed_txns': wallet_details['n_tx'],
            'num_unconfirmed_txns': wallet_details['unconfirmed_n_tx'],
            'num_all_txns': wallet_details['final_n_tx'],
            }
