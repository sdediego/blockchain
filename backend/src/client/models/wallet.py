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
    """
    Storage for cryptocurrency earned by mining blocks or
    received transacations. Keeps track of the balance and
    allowes to make transactions.
    """

    def __init__(self, blockchain: Blockchain = None):
        """
        Create a new wallet instance.

        :param Blockchain blockchain: local copy of the blockchain.
        """
        self.blockchain = blockchain
        self.address = self.generate_address()
        self.private_key = self.generate_private_key()
        self.public_key = self.generate_public_key(self.private_key)

    def __str__(self):
        """"
        Represent class instance via params string.

        :return str: instance representation.
        """
        return ('Wallet('
            f'balance: {self.balance}, '
            f'address: {self.address}, '
            f'public key: {self.public_key})')

    @property
    def balance(self):
        """
        Get the balance for the wallet address.

        :return int: wallet address current available balance.
        """
        return self.get_balance(self.blockchain, self.address)

    @staticmethod
    def generate_address():
        """
        Create a wallet address.

        :return str: string address of 32 hexadecimal digits.
        """
        return uuid.uuid4().hex

    @staticmethod
    def generate_private_key():
        """
        Create private key to sign data.
        """
        return ec.generate_private_key(ec.SECP256K1(), default_backend())

    @staticmethod
    def generate_public_key(private_key: _EllipticCurvePrivateKey):
        """
        Create public key from the private key.
        Public key is used to challenge ownership of cryptocurrency
        and can be shared with the rest of the network.

        :param _EllipticCurvePrivateKey private_key: wallet private key.
        :return str: public key derived from private key.
        """
        public_key = private_key.public_key()
        encoded_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)
        return encoded_key.decode('utf-8')

    @staticmethod
    def verify(public_key: str, signature: tuple, data: dict):
        """
        Verify a signature based on the original public key and data.

        :param str public_key: wallet public key.
        :param tuple signature: data signature candidate.
        :param data: signed data to verify its signature.
        :return bool: wether if signature is valid or not.
        """
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

    @staticmethod
    def get_balance(blockchain: Blockchain, address: str):
        """
        Get the balance for the wallet given address from all the transactions
        data in the blockchain. Thus the balance is calculated by adding the
        output values for the address since the most recent transaction by
        that address.

        :param Blockchain blockchain: blockchain instance.
        :param str address: wallet address to calculate balance for.
        :return int: wallet address current available balance.
        """
        balance = 0
        for block in blockchain.chain:
            for transaction in block.data:
                if transaction['input']['address'] == address:
                    balance = transaction['output'][address]
                elif address in transaction['output']:
                    balance += transaction['output'][address]
        return balance

    def sign(self, data: dict):
        """
        Generate a signature for the data using wallet private key.
        The data signature is a two number tuple representing two coordinates
        of an elliptic curve.

        :param data: data to be signed.
        :return tuple: data signature.
        """
        encoded_data = serialize(data).encode('utf-8')
        signature = self.private_key.sign(encoded_data, ec.ECDSA(hashes.SHA256()))
        return decode_dss_signature(signature)
