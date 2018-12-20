import datetime
import binascii
import requests
import base58

from ethereum import abi

# from tronapi import Tron
# from solc import compile_source

from django.db import models
from django.core.mail import send_mail, EmailMessage
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from lastwill.contracts.submodels.common import *


def convert_address_to_hex(address):
    short_addresss = address[1:]
    decode_address = base58.b58decode(short_addresss)[0:21]
    hex_address = binascii.hexlify(decode_address)
    return hex_address


class TRONContract(EthContract):
    pass


@contract_details('Token contract')
class ContractDetailsTRONToken(CommonDetails):
    token_name = models.CharField(max_length=512)
    token_short_name = models.CharField(max_length=64)
    admin_address = models.CharField(max_length=50)
    decimals = models.IntegerField()
    token_type = models.CharField(max_length=32, default='ERC20')
    tron_contract_token = models.ForeignKey(
        TRONContract,
        null=True,
        default=None,
        related_name='token_details',
        on_delete=models.SET_NULL
    )
    future_minting = models.BooleanField(default=False)
    temp_directory = models.CharField(max_length=36)

    def predeploy_validate(self):
        now = timezone.now()
        token_holders = self.contract.tokenholder_set.all()
        for th in token_holders:
            if th.freeze_date:
                if th.freeze_date < now.timestamp() + 600:
                    raise ValidationError({'result': 1}, code=400)

    @classmethod
    def min_cost(cls):
        network = Network.objects.get(name='TRON_MAINNET')
        cost = cls.calc_cost({}, network)
        return cost

    @staticmethod
    def calc_cost(kwargs, network):
        if NETWORKS[network.name]['is_free']:
            return 0
        result = int(2.99 * 10 ** 18)
        return result

    def get_arguments(self, eth_contract_attr_name):
        return []

    @logging
    def compile(self, eth_contract_attr_name='eth_contract_token'):
        print('standalone token contract compile')
        if self.temp_directory:
            print('already compiled')
            self.lgr.append('already compiled')
            return
        dest, preproc_config = create_directory(self, sour_path='lastwill/tron-token/*')
        self.lgr.append('dest %s' % dest)
        token_holders = self.contract.tokenholder_set.all()
        for th in token_holders:
            if th.address.startswith('41'):
                th.address = '0x' + th.address[2:]
                th.save()
            else:
                th.address = convert_address_to_hex(th.address)
                th.save()
        preproc_params = {"constants": {"D_ONLY_TOKEN": True}}
        preproc_params['constants'] = add_token_params(
            preproc_params['constants'], self, token_holders,
            False, self.future_minting
        )
        owner = '0x' + self.admin_address[2:] if self.admin_address.startswith('41') else convert_address_to_hex(self.admin_address)
        preproc_params['constants']['D_CONTRACTS_OWNER'] = owner
        with open(preproc_config, 'w') as f:
            f.write(json.dumps(preproc_params))
        if os.system('cd {dest} && yarn compile-token'.format(dest=dest)):
            raise Exception('compiler error while deploying')

        with open(path.join(dest, 'build/contracts/MainToken.json'), 'rb') as f:
            token_json = json.loads(f.read().decode('utf-8-sig'))
        with open(path.join(dest, 'build/MainToken.sol'), 'rb') as f:
            source_code = f.read().decode('utf-8-sig')
        tron_contract_token = TRONContract()
        tron_contract_token.abi = token_json['abi']
        tron_contract_token.bytecode = token_json['bytecode'][2:]
        tron_contract_token.compiler_version = token_json['compiler']['version']
        tron_contract_token.contract = self.contract
        tron_contract_token.original_contract = self.contract
        tron_contract_token.source_code = source_code
        tron_contract_token.save()
        self.tron_contract_token = tron_contract_token
        self.save()

    @blocking
    @postponable
    @logging
    def deploy(self, eth_contract_attr_name='eth_contract_token'):
        print('deploy tron token')
        deploy_params = {
            'abi': self.tron_contract_token.abi,
            'bytecode': self.tron_contract_token.bytecode,
            'consume_user_resource_percent': 0,
            'fee_limit': 0,
            'call_value': 0,
            'owner_address': convert_address_to_hex(NETWORKS[self.contract.network]['address']),
            'origin_energy_limit': 10000000
        }
        tron_url = 'http://%s:%s' % (str(NETWORKS[self.contract.network.name]['host']), str(NETWORKS[self.contract.network.name]['port']))
        result = requests.post(tron_url, params=deploy_params)
        print(result)
