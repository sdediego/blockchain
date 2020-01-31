# encoding: utf-8

import uuid
from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.backends.openssl.ec import _EllipticCurvePrivateKey
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (encode_dss_signature,
                                                             decode_dss_signature)

from src.blockchain.models.blockchain import Blockchain
from src.client.models.utils import serialize

# Custom logger for wallet class module
fileConfig(join(dirname(dirname(dirname(__file__))), 'config', 'logging.cfg'))
logger = getLogger(__name__)


class Wallet(object):

    def __init__(self, blockchain: Blockchain = None):
        self.balance = 0
        self.blockchain = blockchain
        self.address = Wallet.generate_address()
        self.private_key = Wallet.generate_private_key()
        self.public_key = Wallet.generate_public_key(self.private_key)

    def __str__(self):
        return ('Wallet('
            f'balance: {self.balance}, '
            f'address: {self.address}, '
            f'public key: {self.public_key})')

    @staticmethod
    def generate_address():
        return uuid.uuid4().hex

    @staticmethod
    def generate_private_key():
        return ec.generate_private_key(ec.SECP256K1(), default_backend())

    @staticmethod
    def generate_public_key(private_key: _EllipticCurvePrivateKey):
        public_key = private_key.public_key()
        encoded_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)
        return encoded_key.decode('utf-8')

    @staticmethod
    def verify(public_key: str, signature: tuple, data):
        encoded_key = public_key.encode('utf-8')
        encoded_sign = encode_dss_signature(*signature)
        encoded_data = serialize(data).encode('utf-8')
        deserialized_key = serialization.load_pem_public_key(encoded_key, default_backend())
        try:
            deserialized_key.verify(encoded_sign, encoded_data, ec.ECDSA(hashes.SHA256()))
        except InvalidSignature:
            logger.warning('[Wallet] Verification error. Invalid signature.')
            return False
        return True

    def sign(self, data):
        encoded_data = serialize(data).encode('utf-8')
        signature = self.private_key.sign(encoded_data, ec.ECDSA(hashes.SHA256()))
        return decode_dss_signature(signature)
