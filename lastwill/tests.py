from lastwill.settings import *

from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory

factory = APIRequestFactory()
request1 = factory.get('/api/get_cost/', {
    'contract_type': '1',
    'heirs_num': 5,
    'heirs': 100,
    'active_to': '9/24/2018 5:03:29 PM'
}, format='json')


request2 = factory.get('/api/balance/', {
    'address': 'dhjbasdbhaabhchbha',
}, format='json')