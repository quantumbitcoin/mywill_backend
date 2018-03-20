from lastwill.settings import *

import unittest
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, APIClient

factory = APIClient()

test_user = User.objects.first()

class TestReceiver(unittest.TestCase):
    def test_get_cost(self):
        request = factory.get('/api/get_cost/', {
            'contract_type': '2',
            'heirs_num': 5,
            'heirs': 100,
            'active_to': 145009888877
        }, format='json')
        assert(request.status_code==200)

    def test_balance(self):
        request = factory.get('/api/balance/', {
            'address': 'dhjbasdbhaabhchbha',
        }, format='json')
        assert(request.status_code==200)

    def test_get_code(self):
        request = factory.get('/api/get_code/', {
            'contract_type': 2,
        }, format='json')
        assert(request.status_code==200)

    def test_test_comp(self):
        request = factory.get('/api/test_comp/', {
            'id': 1,
        }, format='json')
        assert(request.status_code==200)

    def test_get_contract_type(self):
        request = factory.get('/api/get_contract_types/', {
            'id': 1,
        }, format='json')
        assert(request.status_code==200)

    # def test_eth2rub(self):
    #     request = factory.get('/api/eth2rub/')
    #     assert(request.status_code== 200)

    def test_deploy(self):
        request = factory.get('/api/deploy/', {
            'id': 1, 'user': test_user
        }, format='json')
        assert(request.status_code, 200)

    def test_get_token_contracts(self):
        request = factory.get('/api/get_token_contracts/', {
            'user': test_user
        }, format='json')
        assert(request.status_code==200)

    def test_get_statistics(self):
        request = factory.get('/api/get_statistics/')
        assert(request.status_code==200)

    def test_get_contracts(self):
        request = factory.get('/api/contracts')
        assert(request.status_code==200)

    def test_get_sentences(self):
        request = factory.get('/api/sentences')
        assert(request.status_code==200)

    def test_get_one_contract(self):
        request = factory.get('/api/contracts/1')
        assert(request.status_code==200)

    def test_get_one_sentence(self):
        request = factory.get('/api/sentences/1')
        assert(request.status_code==200)

    def test_post_contracts(self):
        request = factory.post('/api/contracts', {
            'user_id': test_user.id,
            'owner_address': 'dsasdadsa',
            'cost': 100,
            'balance': 300,
            'name': 'scacsc',
            'contract_type': 3
        })
        assert(request.status_code==200)

    def test_post_sentences(self):
        request = factory.post('/api/sentences', {
            'username': test_user.username,
            'email': test_user.email,
            'contract_name': 'sdcscs',
            'message': 'czsdcsdsdc'
        })
        assert(request.status_code==200)

    def test_patch_contracts(self):
        request = factory.post('/api/contracts', {
            'user_id': test_user.id,
            'owner_address': 'dsasdadsa',
            'cost': 100,
            'balance': 300,
            'name': 'scacsc',
            'contract_type': 3
        })
        request = factory.patch('/api/contracts/1', {
            'name': 'scacsc'
        })
        assert(request.status_code==200)

    def test_patch_sentences(self):
        request = factory.post('/api/sentences/1', {
            'username': test_user.username,
            'email': test_user.email,
            'contract_name': 'sdcscs',
            'message': 'czsdcsdsdc'
        })
        request = factory.patch('/api/sentences/1', {
            'message': 'czsdcsdsddsdc'
        })
        assert(request.status_code==200)

    def test_put_contracts(self):
        request = factory.post('/api/contracts', {
            'user_id': test_user.id,
            'owner_address': 'dsasdadsa',
            'cost': 100,
            'balance': 300,
            'name': 'scacsc',
            'contract_type': 3
        })
        request = factory.put('/api/contracts/1', {
            'name': 'scacsc'
        })
        assert(request.status_code==200)

    def test_put_sentences(self):
        request = factory.post('/api/sentences/1', {
            'username': test_user.username,
            'email': test_user.email,
            'contract_name': 'sdcscs',
            'message': 'czsdcsdsdc'
        })
        request = factory.put('/api/sentences/1', {
            'message': 'czsdcsdsddsdc'
        })
        assert(request.status_code==200)

    def test_delete_contracts(self):
        request = factory.delete('/api/contracts/1')
        assert(request.status_code==200)

    def test_delete_sentences(self):
        request = factory.delete('/api/sentences/1')
        assert(request.status_code==200)

    # def test_get_discount(self):
    #     request = factory.get('/api/get_discount/', {
    #         'user': test_user,
    #         'contract_type': 2,
    #         'promo': 'SDSDDSD'
    #     })
    #     assert(request.status_code==200)

    def test_resend_email(self):
        request = factory.post('/api/resend_email', {
            'email': test_user.email,
        })
        assert(request.status_code==200)

    def test_count_sold_tokens(self):
        request = factory.post('/api/count_sold_tokens_in_ICO', {
            'address': 'sdvsdvsfdvsdfvsfdvsfd'
        })
        assert(request.status_code==200)

    def test_admin(self):
        request = factory.post('/api/jopa')
        assert(request.status_code==200)
