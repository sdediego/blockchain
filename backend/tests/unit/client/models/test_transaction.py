# encoding: utf-8

import re
import uuid
from unittest.mock import Mock, patch

from src.client.models.transaction import Transaction
from src.client.models.wallet import Wallet
from src.exceptions import TransactionError
from tests.unit.client.utilities import ClientMixin


class TransactionTest(ClientMixin):

    def setUp(self):
        super(TransactionTest, self).setUp()
        self.transaction = Transaction(sender=self.wallet, recipient=self.recipient, amount=self.amount)
        self.transaction_info = self.transaction.info
        self.transaction_attrs = self.transaction_info.keys()

    def test_transaction_string_representation(self):
        self.assertTrue(all([attr in str(self.transaction) for attr in self.transaction_attrs]))

    def test_transaction_generate_uuid(self):
        id = Transaction.generate_uuid()
        self.assertTrue(re.match(r'^[0-9]{,39}$', str(id)))
        self.assertIsInstance(uuid.UUID(int=id), uuid.UUID)

    def test_transaction_generate_output(self):
        output = Transaction.generate_output(self.wallet, self.recipient, self.amount)
        self.assertIsInstance(output, dict)
        self.assertTrue(all([isinstance(key, str) for key in output.keys()]))
        self.assertTrue(all([isinstance(value, float) for value in output.values()]))

    def test_transaction_generate_input(self):
        wallet = Wallet()
        keys = ('timestamp', 'amount', 'address', 'public_key', 'signature')
        input = Transaction.generate_input(wallet, self.transaction.output)
        self.assertIsInstance(input, dict)
        self.assertTrue(all([key in keys for key in input.keys()]))

    def test_transaction_info_property(self):
        attrs = self.transaction.__dict__
        for attr in attrs:
            self.assertIn(attr, self.transaction_info)

    def test_transaction_serialize(self):
        serialized = self.transaction.serialize()
        self.assertIsInstance(serialized, str)
        self.assertTrue(all([attr in serialized for attr in self.transaction_attrs]))

    def test_transaction_deserialize(self):
        serialized = self.transaction.serialize()
        self.assertIsInstance(Transaction.deserialize(serialized), Transaction)

    @patch.object(Transaction, 'is_valid_schema')
    def test_transaction_create_valid_schema(self, mock_is_valid_schema):
        mock_is_valid_schema.return_value = True
        transaction = Transaction.create(**self.transaction_info)
        self.assertTrue(mock_is_valid_schema.called)
        self.assertIsInstance(transaction, Transaction)
        self.assertTrue(all([attr in self.transaction.info.keys() for attr in self.transaction_info.keys()]))
        self.assertTrue(all([value in self.transaction.info.values() for value in self.transaction_info.values()]))

    @patch.object(Transaction, 'is_valid_schema')
    def test_transaction_create_invalid_schema(self, mock_is_valid_schema):
        err_message = 'Validation error.'
        mock_is_valid_schema.side_effect = Mock(side_effect=TransactionError(err_message))
        with self.assertRaises(TransactionError) as err:
            Transaction.create(**self.transaction_info)
            self.assertTrue(mock_is_valid_schema.called)
            self.assertIsInstance(err, TransactionError)
            self.assertIn(err_message, err.message)

    def test_transaction_is_valid_schema(self):
        Transaction.is_valid_schema(self.transaction_info)

    def test_transaction_is_valid_schema_validation_error(self):
        self.transaction_info.pop('input')
        with self.assertRaises(TransactionError) as err:
            Transaction.is_valid_schema(self.transaction_info)
            self.assertIsInstance(err, TransactionError)
            self.assertIn('Validation error.', err.message)

    def test_transaction_update(self):
        recipient = 'recipient'
        balance = self.wallet.balance - self.amount
        amount = self._generate_float(ceil=balance)
        self.transaction.update(self.wallet, recipient, amount)
        self.assertEqual(self.transaction.output[recipient], amount)
        self.assertEqual(self.transaction.output[self.wallet.address], balance - amount)
        self.assertTrue(Wallet.verify(self.transaction.input['public_key'],
                                      self.transaction.input['signature'],
                                      self.transaction.output))

    def test_transaction_update_invalid_amount(self):
        amount = self.wallet.balance
        err_message = 'Invalid amount.'
        with self.assertRaises(TransactionError) as err:
            self.transaction.update(self.wallet, self.recipient, amount)
            self.assertIn(err_message, err.message)
