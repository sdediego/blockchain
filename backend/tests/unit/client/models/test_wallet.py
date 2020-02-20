# encoding: utf-8

import random
import re
import uuid

from cryptography.hazmat.backends.openssl.ec import _EllipticCurvePrivateKey

from src.client.models.wallet import Wallet
from src.config.settings import MINING_REWARD
from tests.unit.client.utilities import ClientMixin


class WalletTest(ClientMixin):

    def setUp(self):
        super(WalletTest, self).setUp()
        self.data = {'test_data_key': 'test_data_value'}

    def test_wallet_string_representation(self):
        attrs = ['address', 'public key']
        self.assertTrue(all([attr in str(self.wallet) for attr in attrs]))

    def test_wallet_generate_address(self):
        address = Wallet.generate_address()
        self.assertTrue(re.match(r'^[a-f0-9]{32}$', address))
        self.assertIsInstance(uuid.UUID(address), uuid.UUID)

    def test_wallet_generate_private_key(self):
        private_key = Wallet.generate_private_key()
        self.assertIsInstance(private_key, _EllipticCurvePrivateKey)

    def test_wallet_generate_public_key(self):
        public_key = Wallet.generate_public_key(self.wallet.private_key)
        self.assertIsInstance(public_key, str)

    def test_wallet_balance(self):
        blocks = random.randint(1, 10)
        self.wallet.blockchain = self._generate_blockchain(blocks)
        self.assertEqual(self.wallet.balance, blocks * MINING_REWARD)

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
