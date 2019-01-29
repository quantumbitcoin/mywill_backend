from lastwill.profile.models import SubSite
from exchange_API import convert, to_wish
from lastwill.consts import NET_DECIMALS
from lastwill.payments.api import calculate_decimals, add_decimals
import unittest
import sys
import ast


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
    def setUp(self):
        self.payment_values = []
        self.currency = self.payment_values[0]
        self.amount = float(self.payment_values[1])
        self.original_amount = float(self.payment_values[2])
        self.site_id = self.payment_values[3]

        self.site_one_currencies = ['ETH', 'BTC', 'WISH', 'BNB']
        self.site_two_currencies = ['ETH', 'BTC', 'EOS', 'EOSISH']
        self.common_currencies = ['ETH', 'BTC']

    def test_01(self):
        print("check payment belongs to first site")
        if self.currency in self.site_one_currencies:
            if self.currency not in self.common_currencies:
                assert(self.site_id  == 1)
            else:
                assert(self.site_id in list(range(1,3)))

    def test_02(self):
        print("check payment belongs to second site")
        if self.currency in self.site_two_currencies:
            if self.currency not in self.common_currencies:
                assert(self.site_id  == 2)
            else:
                assert(self.site_id in list(range(1,3)))

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
    input_values = ast.literal_eval(sys.argv[1])
    PaymentsTests.payment_values = input_values
    unittest.main()

