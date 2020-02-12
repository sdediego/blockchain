# encoding: utf-8

import random

from src.blockchain.models.blockchain import Blockchain
from src.client.models.transaction import Transaction
from src.client.models.transactions_pool import TransactionsPool
from src.client.models.wallet import Wallet
from tests.unit.client.utilities import ClientMixin


class TransactionsPoolTest(ClientMixin):

    def setUp(self):
        self.transactions_pool = self._generate_transactions_pool()
        self.serialized = self.transactions_pool.serialize()

    def _generate_transactions_pool(self):
        pool = {}
        for _ in range(random.randint(1, 10)):
            transaction = self._generate_transaction()
            pool.update({transaction.uuid: transaction})
        return TransactionsPool(pool)

    def _generate_transaction(self):
        wallet = Wallet()
        wallet.balance = self._generate_float()
        recipient = Wallet.generate_address()
        amount = self._generate_float(ceil=wallet.balance)
        return Transaction(sender=wallet, recipient=recipient, amount=amount)

    def test_transactions_pool_string_representation(self):
        uuids = list(self.transactions_pool.pool.keys())
        transactions_pool_str = str(self.transactions_pool)
        self.assertIn('Transactions pool', transactions_pool_str)
        self.assertIn('Transaction', transactions_pool_str)
        self.assertTrue(all([f'uuid: {uuid}' in transactions_pool_str for uuid in uuids]))

    def test_transactions_pool_serialize(self):
        self.assertIsInstance(self.serialized, list)
        self.assertTrue(all([isinstance(transaction, str) for transaction in self.serialized]))

    def test_transactions_pool_deserialize(self):
        deserialized = TransactionsPool.deserialize(self.serialized)
        self.assertIsInstance(deserialized, TransactionsPool)
        self.assertTrue(hasattr(deserialized, 'pool'))
        self.assertListEqual(list(deserialized.pool.keys()), list(self.transactions_pool.pool.keys()))

    def test_transactions_pool_get_transaction(self):
        initial = random.choice(list(self.transactions_pool.pool.values()))
        address = initial.input.get('address')
        transaction = self.transactions_pool.get_transaction(address)
        self.assertEqual(transaction.uuid, initial.uuid)

    def test_transactions_pool_get_transaction_not_exists(self):
        address = 'address'
        transaction = self.transactions_pool.get_transaction(address)
        self.assertIsNone(transaction)

    def test_transactions_pool_add_transaction(self):
        initial_size = self.transactions_pool.size
        transaction = self._generate_transaction()
        self.assertNotIn(transaction.uuid, self.transactions_pool.pool)
        self.transactions_pool.add_transaction(transaction)
        self.assertEqual(self.transactions_pool.size, initial_size + 1)
        self.assertIn(transaction.uuid, self.transactions_pool.pool)
        self.transactions_pool.add_transaction(transaction)
        self.assertEqual(self.transactions_pool.size, initial_size + 1)
        self.assertIn(transaction.uuid, self.transactions_pool.pool)
