import requests
import os
import hashlib
import binascii

from bip32utils import BIP32Key
from eth_keys import keys

from rest_framework.exceptions import PermissionDenied
from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer
from rest_auth.serializers import (
    LoginSerializer, PasswordChangeSerializer, PasswordResetConfirmSerializer
)

from lastwill.profile.models import Profile, UserSiteBalance, SubSite
from lastwill.settings import ROOT_PUBLIC_KEY, ROOT_PUBLIC_KEY_EOSISH, BITCOIN_URLS, MY_WISH_URL, EOSISH_URL, TRON_URL, ROOT_PUBLIC_KEY_TRON, ROOT_PUBLIC_KEY_SWAPS, SWAPS_URL
from lastwill.profile.helpers import valid_totp


def generate_memo(m):
    memo_str = os.urandom(8)
    m.update(memo_str)
    memo_str = binascii.hexlify(memo_str + m.digest()[0:2])
    return memo_str


def registration_btc_address(btc_address):
    requests.post(
        BITCOIN_URLS['main'],
        json={
            'method': 'importaddress',
            'params': [btc_address, btc_address, False],
            'id': 1, 'jsonrpc': '1.0'
        }
    )


def create_wish_balance(user, eth_address, btc_address, memo_str):
    wish = SubSite.objects.get(site_name=MY_WISH_URL)
    UserSiteBalance(
        user=user, subsite=wish,
        eth_address=eth_address,
        btc_address=btc_address,
        tron_address='41' + eth_address[2:],
        memo=memo_str
    ).save()


def create_eosish_balance(user, eth_address, btc_address, memo_str):
    eosish = SubSite.objects.get(site_name=EOSISH_URL)
    UserSiteBalance(
        user=user, subsite=eosish,
        eth_address=eth_address,
        btc_address=btc_address,
        memo=memo_str
    ).save()


def create_tron_balance(user, eth_address, btc_address, memo_str):
    tron = SubSite.objects.get(site_name=TRON_URL)
    UserSiteBalance(
        user=user, subsite=tron,
        eth_address=eth_address,
        btc_address=btc_address,
        tron_address='41' + eth_address[2:],
        memo=memo_str
    ).save()


def create_swaps_balance(user, eth_address, btc_address, memo_str):
    swaps = SubSite.objects.get(site_name=SWAPS_URL)
    UserSiteBalance(
        user=user, subsite=swaps,
        eth_address=eth_address,
        btc_address=btc_address,
        tron_address='41' + eth_address[2:],
        memo=memo_str
    ).save()


def init_profile(user, is_social=False, metamask_address=None, lang='en'):
    m = hashlib.sha256()
    memo_str1 = generate_memo(m)
    # memo_str2 = generate_memo(m)
    # memo_str3 = generate_memo(m)
    memo_str4 = generate_memo(m)

    wish_key = BIP32Key.fromExtendedKey(ROOT_PUBLIC_KEY, public=True)
    # eosish_key = BIP32Key.fromExtendedKey(ROOT_PUBLIC_KEY_EOSISH, public=True)
    # tron_key = BIP32Key.fromExtendedKey(ROOT_PUBLIC_KEY_TRON, public=True)
    swaps_key = BIP32Key.fromExtendedKey(ROOT_PUBLIC_KEY_SWAPS, public=True)

    btc_address1 = wish_key.ChildKey(user.id).Address()
    # btc_address2 = eosish_key.ChildKey(user.id).Address()
    # btc_address3 = tron_key.ChildKey(user.id).Address()
    btc_address4 = swaps_key.ChildKey(user.id).Address()
    eth_address1 = keys.PublicKey(wish_key.ChildKey(user.id).K.to_string()).to_checksum_address().lower()
    # eth_address2 = keys.PublicKey(eosish_key.ChildKey(user.id).K.to_string()).to_checksum_address().lower()
    # eth_address3 = keys.PublicKey(tron_key.ChildKey(user.id).K.to_string()).to_checksum_address().lower()
    eth_address4 = keys.PublicKey(swaps_key.ChildKey(user.id).K.to_string()).to_checksum_address().lower()

    Profile(user=user, is_social=is_social, metamask_address=metamask_address, lang=lang).save()
    create_wish_balance(user, eth_address1, btc_address1, memo_str1)
    # create_eosish_balance(user, eth_address2, btc_address2, memo_str2)
    # create_tron_balance(user, eth_address3, btc_address3, memo_str3)
    create_swaps_balance(user, eth_address4, btc_address4, memo_str4)
    registration_btc_address(btc_address1)
    # registration_btc_address(btc_address2)
    # registration_btc_address(btc_address3)
    registration_btc_address(btc_address4)


class UserRegisterSerializer(RegisterSerializer):
    def save(self, request):
        user = super().save(request)
        init_profile(user, lang=request.COOKIES.get('lang', 'en'))
        return user


class UserLoginSerializer2FA(LoginSerializer):
    totp = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        res = super().validate(attrs)
        if attrs['user']:
            user = attrs['user']
            if user.profile.use_totp:
                totp = attrs.get('totp', None)
                if not totp:
                    raise PermissionDenied(1019)
                if not valid_totp(user, totp):
                    raise PermissionDenied(1020)
        return res


class PasswordChangeSerializer2FA(PasswordChangeSerializer):
    totp = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        res = super().validate(attrs)
        if self.user.profile.use_totp:
            totp = attrs.get('totp', None)
            if totp is None or not valid_totp(self.user, totp):
                raise PermissionDenied()
        return res


class PasswordResetConfirmSerializer2FA(PasswordResetConfirmSerializer):
    totp = serializers.CharField(required=False, allow_blank=True)

    def custom_validation(self, attrs):
        if self.user.profile.use_totp:
            totp = attrs.get('totp', None)
            if not totp:
                raise PermissionDenied(1021)
            if not valid_totp(self.user, totp):
                raise PermissionDenied(1022)
