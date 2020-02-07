# encoding: utf-8

import json
import random
from unittest.mock import Mock, patch

from pydantic import ValidationError

from src.client.models.wallet import Wallet
from src.client.schemas.transaction import TransactionSchema
from tests.unit.logging import LoggingMixin


class TransactionSchemaTest(LoggingMixin):

    def setUp(self):
        self.sender = Wallet()
    
    def _generate_float(self, floor: float = 0, ceil: float = 100):
        return random.uniform(floor, ceil)

    def test_transactionschema_valid_arguments(self):
        self.sender.balance = self._generate_float()
        valid_arguments = {
            'sender': self.sender,
            'recipient': Wallet.generate_address(),
            'amount': self._generate_float(ceil=self.sender.balance)
        }
        transactionschema = TransactionSchema(**valid_arguments)
        self.assertIsInstance(transactionschema, TransactionSchema)
        self.assertIsInstance(transactionschema.sender, Wallet)
        self.assertIsInstance(transactionschema.recipient, str)
        self.assertIsInstance(transactionschema.amount, float)

    def test_transactionschema_invalid_arguments_types(self):
        invalid_arguments_types = {
            'sender': 's3nd3r',
            'recipient': 100,
            'amount': 'am0un7'
        }
        with self.assertRaises(ValidationError) as err:
            TransactionSchema(**invalid_arguments_types)
            errors = json.loads(err.json())
            self.assertEqual(len(errors), len(invalid_arguments_types.keys()))
            self.assertTrue(all([error.get('type') in ['type_error', 'value_error'] for error in errors]))

    def test_transactionschema_invalid_arguments_values(self):
        invalid_arguments_values = {
            'sender': self.sender,
            'recipient': 'r3c1p13n7',
            'amount': self.sender.balance - self._generate_float()
        }
        with self.assertRaises(ValidationError) as err:
            TransactionSchema(**invalid_arguments_values)
            errors = json.loads(err.json())
            self.assertEqual(len(errors), len(invalid_arguments_values.keys()))
            self.assertTrue(all([error.get('type') ==  'value_error' for error in errors]))
