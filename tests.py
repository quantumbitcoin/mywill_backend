import unittest
import datetime

from receiver import *
from django.contrib.auth.models import User
from lastwill.profile.models import Profile
from lastwill.contracts.serializers import ContractSerializer
from lastwill.contracts.models import EthContract, Contract, ContractDetailsLostKey


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

        test_ethcontract = EthContract(
            address='hjbjvjmv', contract=test_base_contract
        )
        test_ethcontract.save()
        test_contract = EthContract.objects.all().first()
        test_message = {'contractId': test_contract.id}
        killed(test_message)
        result_contract = EthContract.objects.get(id=test_contract.id)
        self.assertEqual(result_contract.contract.state, 'KILLED')

    def test_triggered(self):
        test_user = User(
            email='no11@no.no',
            username='ffff',
            password='ffffff'
        )
        test_user.save()

        test_base_contract = Contract(
            name='sdvsdvdddasdvfdsv', address='dfasdfdfdvsvafva', cost=10,
            owner_address='dfcasdfdfdfdfcvs', user_address='jlhgkgfgfgdfgv',
            user_id=test_user.id, contract_type=1
        )
        test_base_contract.save()
        # base_contract=Contract.objects.all().first()
        # test_common_details = CommonDetails(contract_id=test_base_contract.id)
        # test_common_details.save()

        test_ethcontract = EthContract(
            address='hjbwdaddsjvjmv',
            contract=test_base_contract
        )
        test_ethcontract.save()
        test_details = ContractDetailsLostKey(
            user_address='dfasdfdfdvsvafva',
            eth_contract=test_ethcontract,
            check_interval=100,
            active_to=datetime.date.today(),
            contract_id=test_ethcontract.id
        )
        test_details.save()
        test_contract = EthContract.objects.get(id=test_ethcontract.id)
        test_message = {'contractId': test_contract.id}
        triggered(test_message)
        result_contract = EthContract.objects.get(id=test_contract.id)
        self.assertEqual(result_contract.contract.state, 'TRIGGERED')

    def test_deployed(self):
        test_user = User(
            email='no111@no.no',
            username='ffffff',
            password='ffffff'
        )
        test_user.save()

        test_base_contract = Contract(
            name='sdvsdvdddasdvfdsv', address='dfasdfdfdvsvafva', cost=10,
            owner_address='dfcasdfdfdfdfcvs', user_address='jlhgkgfgfgdfgv',
            user_id=test_user.id, contract_type=1
        )
        test_base_contract.save()

        # test_common_details = CommonDetails(contract_id=test_base_contract.id)
        # test_common_details.save()

        test_ethcontract = EthContract(
            address='hjbwdaddsjvjmv',
            contract=test_base_contract
        )
        test_ethcontract.save()
        test_contract = EthContract.objects.get(id=test_ethcontract.id)
        test_details = ContractDetailsLostKey(
            user_address='dfasdfdfdvsvafva',
            eth_contract=test_ethcontract,
            check_interval=100,
            active_to=datetime.date.today(),
            contract_id=test_ethcontract.id
        )
        test_details.save()
        test_message = {
            'contractId': test_contract.id,
            'address': 'sdjfn;kjdbldjbslkjdbs'
                        }
        deployed(test_message)
        result_contract = EthContract.objects.get(id=test_contract.id)
        self.assertEqual(result_contract.contract.state, 'ACTIVE')

    def test_launch(self):
        test_user = User(
            email='no11111@no.no',
            username='ffffffff',
            password='ffffffff'
        )
        test_user.save()

        test_base_contract = Contract(
            name='sdvsdvdddasdsgvfv', address='dfafdfdvsvafva', cost=10,
            owner_address='dfcasdfdfdvs', user_address='jlfgfgdfgv',
            user_id=test_user.id, contract_type=1
        )
        test_base_contract.save()

        # test_common_details = CommonDetails(contract_id=test_base_contract.id)
        # test_common_details.save()

        test_ethcontract = EthContract(
            address='hjbwdaddsjfddfvjmv',
            contract=test_base_contract
        )
        test_ethcontract.save()
        test_contract = EthContract.objects.get(id=test_ethcontract.id)
        test_details = ContractDetailsLostKey(
            user_address='dfasdfdfdvsvafva',
            eth_contract=test_ethcontract,
            check_interval=100,
            active_to=datetime.date.today(),
            contract_id=test_ethcontract.id
        )
        test_details.save()
        test_message = {
            'contractId': test_contract.id,
            'address': 'sdjfn;kjdbddldjbslkjdbs'
                        }
        launch(test_message)
        result_contract = EthContract.objects.get(id=test_contract.id)
        self.assertEqual(
            result_contract.contract.state, 'WAITING_FOR_DEPLOYMENT'
        )


if __name__ == '__main__':
    unittest.main()
