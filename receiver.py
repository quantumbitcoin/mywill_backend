import pika
import os
import traceback
import threading
import json
import sys
from types import FunctionType

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lastwill.settings')
import django
django.setup()
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from lastwill.contracts.models import (
    Contract, EthContract, TxFail, NeedRequeue, AlreadyPostponed
)
from lastwill.settings import NETWORKS, test_logger
from lastwill.deploy.models import DeployAddress
from lastwill.payments.api import create_payment
from exchange_API import to_wish


class Receiver(threading.Thread):

    def __init__(self, network=None):
        super().__init__()
        if network is None:
            if len(sys.argv) > 1 and sys.argv[1] in NETWORKS:
                self.network = sys.argv[1]
        else:
            self.network = network

    def run(self):
        print('run  receiver for', self.network, flush=True)
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            'localhost',
            5672,
            'mywill',
            pika.PlainCredentials('java', 'java'),
            heartbeat_interval=0,
        ))
        self.channel = connection.channel()
        self.channel.queue_declare(
                queue=NETWORKS[self.network]['queue'],
                durable=True,
                auto_delete=False,
                exclusive=False
            )
        self.channel.basic_consume(self.callback, queue=NETWORKS[net]['queue'])
        self.channel.start_consuming()

    # @logging
    def payment(self, message):
        print('payment message', flush=True)
        print('message["amount"]', message['amount'])
        value = message['amount'] if message['currency'] == 'WISH' else to_wish(
                message['currency'], message['amount']
        )
        print(value)
        print('payment ok', flush=True)
        create_payment(message['userId'], value, message['transactionHash'], message['currency'], message['amount'])

    # @logging
    def deployed(self, message):
        print('deployed message received', flush=True)
        contract = EthContract.objects.get(id=message['contractId']).contract
        contract.get_details().msg_deployed(message)
        print('deployed ok!', flush=True)

    # @logging
    def killed(self, message):
        print('killed message', flush=True)
        contract = EthContract.objects.get(id=message['contractId']).contract
        contract.state = 'KILLED'
        contract.save()
        network = contract.network
        DeployAddress.objects.filter(network=network, locked_by=contract.id).update(locked_by=None)
        print('killed ok', flush=True)

    # @logging
    def checked(self, message):
        print('checked message', flush=True)
        contract = EthContract.objects.get(id=message['contractId']).contract
        contract.get_details().checked(message)
        print('checked ok', flush=True)

    # @logging
    def repeat_check(self, message):
        print('repeat check message', flush=True)
        contract = EthContract.objects.get(id=message['contractId']).contract
        contract.get_details().check_contract()
        print('repeat check ok', flush=True)

    # @logging
    def check_contract(self, message):
        print('check contract message', flush=True)
        contract = Contract.objects.get(id=message['contractId'])
        contract.get_details().check_contract()
        print('check contract ok', flush=True)

    # @logging
    def triggered(self, message):
        print('triggered message', flush=True)
        contract = EthContract.objects.get(id=message['contractId']).contract
        contract.get_details().triggered(message)
        print('triggered ok', flush=True)

    # @logging
    def launch(self, message):
        print('launch message', flush=True)
        try:
            contract_details = Contract.objects.get(id=message['contractId']).get_details()
            contract_details.deploy()
        except ObjectDoesNotExist:
            # only when contract removed manually
            print('no contract, ignoging')
            return
        contract_details.refresh_from_db()
        print('launch ok')

    # @logging
    def ownershipTransferred(self, message):
        print('ownershipTransferred message')
        contract = EthContract.objects.get(id=message['crowdsaleId']).contract
        contract.get_details().ownershipTransferred(message)
        print('ownershipTransferred ok')

    # @logging
    def initialized(self, message):
        print('initialized message')
        contract = EthContract.objects.get(id=message['contractId']).contract
        contract.get_details().initialized(message)
        print('initialized ok')

    # @logging
    def finish(self, message):
        print('finish message')
        contract = EthContract.objects.get(id=message['contractId']).contract
        contract.get_details().finalized(message)
        print('finish ok')

    # @logging
    def finalized(self, message):
        print('finalized message')
        contract = EthContract.objects.get(id=message['contractId']).contract
        contract.get_details().finalized(message)
        print('finalized ok')

    # @logging
    def transactionCompleted(self, message):
        print('transactionCompleted')
        if message['transactionStatus']:
            print('success, ignoring')
            return
        try:
            contract = EthContract.objects.get(tx_hash=message['transactionHash']).contract
            contract.get_details().tx_failed(message)
        except Exception as e:
            print(e)
            print('not found, returning')
            return
        print('transactionCompleted ok')

    # @logging
    def cancel(self, message):
        print('cancel message')
        contract = Contract.objects.get(id=message['contractId'])
        contract.get_details().cancel(message)
        print('cancel ok')

    # @logging
    def confirm_alive(self, message):
        print('confirm_alive message')
        contract = Contract.objects.get(id=message['contractId'])
        contract.get_details().i_am_alive(message)
        print('confirm_alive ok')

    # @logging
    def contractPayment(self, message):
        print('contract Payment message')
        contract = Contract.objects.get(id=message['contractId'])
        contract.get_details().contractPayment(message)
        print('contract Payment ok')

    # @logging
    def notified(self, message):
        print('notified message')
        contract = EthContract.objects.get(id=message['contractId']).contract
        details = contract.get_details()
        details.last_reset = timezone.now()
        details.save()
        print('notified ok')

    # @logging
    def fundsAdded(self, message):
        print('funds Added message')
        contract = EthContract.objects.get(id=message['contractId']).contract
        contract.get_details().fundsAdded(message)
        print('funds Added ok')

    # @logging
    def make_payment(self, message):
        print('make payment message')
        contract = Contract.objects.get(id=message['contractId'])
        contract.get_details().make_payment(message)
        print('make payment ok')

    def timesChanged(self, message):
        print('time changed message')
        contract = EthContract.objects.get(id=message['contractId']).contract
        contract.get_details().timesChanged(message)
        print('time changed ok')

    # @logging
    def callback(self, ch, method, properties, body):
        print('received', body, properties, method, flush=True)
        try:
            message = json.loads(body.decode())
            if message.get('status', '') == 'COMMITTED':
                getattr(self, properties.type, self.unknown_handler)(message)
        except (TxFail, AlreadyPostponed):
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except NeedRequeue:
            print('requeueing message', flush=True)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        except Exception as e:
            print('\n'.join(traceback.format_exception(*sys.exc_info())),
                  flush=True)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    # @logging
    def unknown_handler(self, message):
        print('unknown message', message, flush=True)


def methods(cls):
    return [x for x, y in cls.__dict__.items() if type(y) == FunctionType and not x.startswith('_')]


"""
rabbitmqctl add_user java java
rabbitmqctl add_vhost mywill
rabbitmqctl set_permissions -p mywill java ".*" ".*" ".*"
"""

# channel = connection.channel()
print('receiver started', flush=True)
nets = NETWORKS.keys()
for net in nets:
    rec = Receiver(net)
    # channel.queue_declare(
    #     queue=NETWORKS[net]['queue'],
    #     durable=True,
    #     auto_delete=False,
    #     exclusive=False
    # )
    # rec.channel.basic_consume(rec.callback, queue=NETWORKS[net]['queue'])
    rec.start()
