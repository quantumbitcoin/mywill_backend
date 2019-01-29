#from lastwill.profile.models import SubSite
#from exchange_API import convert, to_wish
#from lastwill.consts import NET_DECIMALS
#from lastwill.payments.api import calculate_decimals, add_decimals
import unittest
import sys
import ast
import json
import requests

NET_DECIMALS = {
    'ETH': 10 ** 18,
    'ETH_GAS_PRICE': 10 ** 9,
    'EOS': 10 ** 4,
    'WISH': 10 ** 18,
    'EOSISH': 10 ** 4,
    'BNB': 10 ** 18,
    'BTC': 10 ** 8
}

def convert(fsym, tsyms):
    eosish_factor = 1.0
    revesre_convert = False
    allowed = {'WISH', 'USD', 'ETH', 'EUR', 'BTC', 'NEO', 'EOS', 'EOSISH', 'BNB', 'TRX'}
    if fsym == 'EOSISH' or tsyms == 'EOSISH':
        eosish_factor = float(
        requests.get('https://api.chaince.com/tickers/eosisheos/',
                     headers={'accept-version': 'v1'}).json()['price']
        )
        print('eosish factor', eosish_factor, flush=True)
        if fsym == 'EOSISH':
            fsym = 'EOS'
            if tsyms == fsym:
                return {'EOS': eosish_factor}
        else:
            tsyms = 'EOS'
            if tsyms == fsym:
                return {'EOSISH': 1 / eosish_factor}
            revesre_convert = True
            eosish_factor = 1 / eosish_factor

    if fsym not in allowed or any([x not in allowed for x in tsyms.split(',')]):
        raise Exception('currency not allowed')
    print(fsym, tsyms)
    answer = json.loads(requests.get(
        'http://127.0.0.1:5001/convert?fsym={fsym}&tsyms={tsyms}'.format(fsym=fsym, tsyms=tsyms)
    ).content.decode())
    print('currency_proxi answer', answer, flush=True)
    if revesre_convert:
        answer = {'EOSISH': answer['EOS']}
        tsyms = 'EOSISH'
    answer[tsyms] = answer[tsyms] * eosish_factor
    return answer


def to_wish(curr, amount=1):
    return amount * (convert(curr, 'WISH')['WISH'])


def calculate_decimals(currency, amount):
    # count sum payments without decimals
    if currency in ['ETH']:
        amount = amount / NET_DECIMALS['ETH']
    if currency in ['BTC']:
        amount = amount / NET_DECIMALS['BTC']
    if currency in ['EOS']:
        amount = amount / NET_DECIMALS['EOS']
    return amount


def add_decimals(currency, amount):
    # add decimals for eth, btc
    if currency in ['ETH']:
        amount = amount * NET_DECIMALS['ETH']
    if currency in ['BTC']:
        amount = amount * NET_DECIMALS['BTC']
    return amount



def from_wish(curr, amount=1):
    return amount * (convert('WISH', curr)[curr])


def convert_currency(amount, currency, site_id):
    if site_id == 1:
        converted_amount = to_wish(currency, amount)
    elif site_id == 2:
        converted_amount = calculate_decimals(currency, amount) * convert(currency, 'EOSISH')['EOSISH']
        converted_amount *= NET_DECIMALS['EOSISH']
    return float(converted_amount)


def recalculate_amount(amount, currency, site_id):
    checked_amount = convert_currency(amount, currency, site_id)
    if 0.98 <= (amount / checked_amount) <= 1.02:
        return True
    else:
        return False


class PaymentsTests(unittest.TestCase):
    payment_values = []

    def setUp(self):
        self.amount = float(self.payment_values[0])
        self.original_amount = float(self.payment_values[1])
        self.currency = self.payment_values[2]
        self.site_id = int(self.payment_values[3])

        self.site_one_currencies = ['ETH', 'BTC', 'WISH', 'BNB']
        self.site_two_currencies = ['ETH', 'BTC', 'EOS', 'EOSISH']
        self.common_currencies = ['ETH', 'BTC']
        self.sites_list = list(range(1,3))

    def test_01(self):
        print("check payment belongs to first site")
        if self.currency in self.site_one_currencies:
            if self.currency not in self.common_currencies:
                self.assertEqual(self.site_id, 1)
            else:
                self.assertTrue(self.site_id in self.sites_list)

    def test_02(self):
        print("check payment belongs to second site")
        if self.currency in self.site_two_currencies:
            if self.currency not in self.common_currencies:
                self.assertEqual(self.site_id, 2)
            else:
                self.assertTrue(self.site_id in self.sites_list)

    def test_03(self):
        if self.site_id != 1:
            pass
        else:
            if self.currency not in ['ETH', 'BNB']:
                pass
            else:
                self.assertTrue(recalculate_amount(self.original_amount, self.currency, self.site_id))

    def test_04(self):
        if self.site_id != 1:
            pass
        else:
            if self.currency != 'BTC':
                pass
            else:
                prechecked_amount = convert_currency(self.original_amount, 'BTC', self.site_id)
                prechecked_amount *= (NET_DECIMALS['ETH'] / NET_DECIMALS['BTC'])
                self.assertTrue(0.98 <= (self.amount / prechecked_amount) <= 1.02)

    def test_05(self):
        if self.site_id != 1:
            pass
        else:
            if self.currency != 'WISH':
                pass
            else:
                self.assertTrue(self.amount == self.original_amount)

    def test_06(self):
        if self.site_id != 2:
            pass
        else:
            if self.currency not in ['ETH', 'BTC']:
                pass
            else:
                prechecked_amount = convert_currency(self.original_amount, self.currency, self.site_id)
                prechecked_amount = add_decimals(self.currency, prechecked_amount)
                self.assertTrue(0.98 <= (self.amount / prechecked_amount) <= 1.02)

    def test_07(self):
        if self.site_id != 2:
            pass
        else:
            if self.currency != 'EOS':
                pass
            else:
                self.assertTrue(recalculate_amount(self.original_amount, self.currency, self.site_id))

    def test_08(self):
        if self.site_id != 1:
            pass
        else:
            if self.currency != 'EOSISH':
                pass
            else:
                self.assertTrue(self.amount == self.original_amount)


if __name__ == "__main__":
    input_values = []
    input_values.append(sys.argv.pop())
    input_values.append(sys.argv.pop())
    input_values.append(sys.argv.pop())
    input_values.append(sys.argv.pop())
    input_values.reverse()
    print(input_values)
    PaymentsTests.payment_values = input_values
    unittest.main()

