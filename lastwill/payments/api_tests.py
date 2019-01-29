from lastwill.profile.models import SubSite
from exchange_API import convert, to_wish
from lastwill.consts import NET_DECIMALS
from lastwill.payments.api import calculate_decimals, add_decimals


def from_wish(curr, amount=1):
    return amount * (convert('WISH', curr)[curr])


def convert_currency(amount, currency, site_id):
    if site_id == 1:
        converted_amount = to_wish(currency, amount)
    elif site_id == 2:
        converted_amount = calculate_decimals(currency, amount) * convert(currency, 'EOSISH')['EOSISH']
        converted_amount *= NET_DECIMALS['EOSISH']
    return float(converted_amount)


def recalculated_amount(amount, currency, site_id):
    checked_amount = convert_currency(amount, currency, site_id)
    if 0.98 <= (amount / checked_amount) <= 1.02:
        return amount
    else:
        return checked_amount


def check_payment(currency, amount, original_amount, original_site_id):
    site_one_currencies = ['ETH', 'BTC', 'WISH', 'BNB']
    site_two_currencies = ['ETH', 'BTC', 'EOS', 'EOSISH']
    common_currencies = ['ETH', 'BTC']
    amount = float(amount)
    exchange_price = amount / original_amount
    site_id = original_site_id

    if currency in site_one_currencies and original_site_id != 1:
        if currency not in common_currencies:
            site_id = 1

    if currency in site_two_currencies and original_site_id != 2:
        if currency not in common_currencies:
            site_id = 2

    if site_id == 1:
        if currency in ['ETH', 'BNB']:
            new_amount = recalculated_amount(original_amount, currency, site_id)
        elif currency == 'BTC':
            new_amount = recalculated_amount(original_amount, 'BTC', site_id)
            new_amount *= (NET_DECIMALS['ETH'] / NET_DECIMALS['BTC'])
        elif currency == 'WISH':
            if amount != original_amount:
                new_amount = original_amount

    if site_id == 2:
        if currency in ['ETH', 'BTC']:
            new_amount = recalculated_amount(original_amount, currency, site_id)
            new_amount = add_decimals(currency, new_amount)
        elif currency == 'EOS':
            new_amount = recalculated_amount(original_amount, currency, site_id)
        elif currency == 'EOSISH':
            if amount != original_amount:
                new_amount = original_amount

    return {'checked_amount': new_amount, 'checked_site_id': site_id}






