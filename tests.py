import unittest

from receiver import *
from django.contrib.auth.models import User
from lastwill.profile.models import Profile
from lastwill.contracts.models import EthContract, Contract


class TestReceiver(unittest.TestCase):
    def test_payment(self):
        test_user = User(
            email='no@no.no',
            username='f',
            password='ff'
        )
        test_user.save()
        test_profile = Profile(
            user_id=test_user.id,
            balance=0,
            internal_address='hbjbljbljhb',
            internal_btc_address='dfvsfvafvewva'
        )
        test_profile.save()
        test_message = {
            'currency': 'WISH',
            'amount': 100,
            'userId': test_user.id
        }
        payment(test_message)
        result_profile = Profile.objects.get(id=test_profile.id)
        self.assertEqual(result_profile.balance, 100)

    def test_killed(self):
        test_user = User(
            email='no1@no.no',
            username='fff',
            password='fffff'
        )
        test_user.save()

        test_base_contract = Contract(
            name='sdvsdvsv', address='dfasdvsvafva', cost=10,
            owner_address='dfcasdcvs', user_address='jlhgkgv',
            user_id=test_user.id
        )
        test_base_contract.save()

        test_ethcontract = EthContract(address='hjbjvjmv', contract=test_base_contract)
        test_ethcontract.save()
        test_contract = EthContract.objects.all().first()
        test_message = {'contractId': test_contract.id}
        killed(test_message)
        result_contract = EthContract.objects.get(id=test_contract.id)
        self.assertEqual(result_contract.contract.state, 'KILLED')

if __name__ == '__main__':
    unittest.main()
