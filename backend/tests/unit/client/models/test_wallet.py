# encoding: utf-8

import re
import uuid
from unittest import TestCase

from cryptography.hazmat.backends.openssl import ec

from src.client.models.wallet import Wallet
from tests.unit.logging import LoggingMixin


class WalletTest(LoggingMixin):

    def setUp(self):
        self.wallet = Wallet()
        self.data = {'test_data_key': 'test_data_value'}

    def test_wallet_string_representation(self):
        attrs = ['balance', 'address', 'public key']
        self.assertTrue(all([attr in str(self.wallet) for attr in attrs]))

    def test_wallet_generate_address(self):
        address = Wallet.generate_address()
        self.assertTrue(re.match(r'^[a-f0-9]{32}$', address))
        self.assertIsInstance(uuid.UUID(address), uuid.UUID)

    def test_wallet_generate_private_key(self):
        private_key = Wallet.generate_private_key()
        self.assertIsInstance(private_key, ec._EllipticCurvePrivateKey)

    def test_wallet_generate_public_key(self):
        public_key = Wallet.generate_public_key(self.wallet.private_key)
        self.assertIsInstance(public_key, str)

    def test_wallet_sign(self):
        signature = self.wallet.sign(self.data)
        self.assertIsInstance(signature, tuple)
        self.assertEqual(len(signature), 2)
        self.assertTrue(all([isinstance(coordinate, int) for coordinate in signature]))

    def test_wallet_verify_valid_signature(self):
        signature = self.wallet.sign(self.data)
        self.assertTrue(Wallet.verify(self.wallet.public_key, signature, self.data))

    def test_wallet_verify_invalid_signature(self):
        signature = self.wallet.sign(self.data)
        self.assertFalse(Wallet.verify(Wallet().public_key, signature, self.data))
