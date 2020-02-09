# encoding: utf-8

import json
import random
import uuid

from pydantic import ValidationError

from src.client.models.utils import get_utcnow_timestamp
from src.client.models.wallet import Wallet
from src.client.schemas.transaction import TransactionSchema
from tests.unit.client.utilities import ClientMixin


class TransactionSchemaTest(ClientMixin):

    def setUp(self):
        super(TransactionSchemaTest, self).setUp()
        self.output = self._generate_output()
        self.input = self._generate_input()

    def _generate_address(self):
        return Wallet.generate_address()

    def _generate_uuid(self):
        return uuid.uuid4().int

    def _generate_output(self):
        output = {}
        output[self.recipient] = self.amount
        output[self.wallet.address] = self.wallet.balance - self.amount
        return output

    def _generate_input(self):
        input = {}
        input['timestamp'] = get_utcnow_timestamp()
        input['amount'] = self.wallet.balance
        input['address'] = self.wallet.address
        input['public_key'] = self.wallet.public_key
        input['signature'] = self.wallet.sign(self.output)
        return input

    def test_transactionschema_valid_uuid_output_input(self):
        valid_arguments = {
            'uuid': self._generate_uuid(),
            'output': self.output,
            'input': self.input
        }
        transactionschema = TransactionSchema(**valid_arguments)
        self.assertIsInstance(transactionschema, TransactionSchema)
        self.assertIsInstance(transactionschema.uuid, int)
        self.assertIsInstance(transactionschema.output, dict)
        self.assertIsInstance(transactionschema.input, dict)

    def test_transactionschema_valid_sender_recipient_amount(self):
        valid_arguments = {
            'sender': self.wallet,
            'recipient': self._generate_address(),
            'amount': self.amount
        }
        transactionschema = TransactionSchema(**valid_arguments)
        self.assertIsInstance(transactionschema, TransactionSchema)
        self.assertIsInstance(transactionschema.sender, Wallet)
        self.assertIsInstance(transactionschema.recipient, str)
        self.assertIsInstance(transactionschema.amount, float)

    def test_transactionschema_invalid_arguments_set(self):
        valid_arguments = [{
            'uuid': self._generate_uuid(),
            'output': self.output,
            'input': self.input
        },{
            'sender': self.wallet,
            'recipient': self._generate_address(),
            'amount': self.amount
        }]
        arguments = random.choice(valid_arguments)
        key = random.choice(list(arguments.keys()))
        arguments.pop(key)
        with self.assertRaises(ValidationError) as err:
            TransactionSchema(**arguments)
            errors = json.loads(err.json())
            self.assertEqual(len(errors), 1)
            self.assertTrue(errors[0].get('type') == 'value_error')

    def test_transactionschema_invalid_uuid_output_input_types(self):
        invalid_arguments_types = {
            'uuid': 'uuid',
            'output': 'output',
            'input': 'input'
        }
        with self.assertRaises(ValidationError) as err:
            TransactionSchema(**invalid_arguments_types)
            errors = json.loads(err.json())
            self.assertEqual(len(errors), len(invalid_arguments_types.keys()))
            self.assertTrue(all([error.get('type') in ['type_error', 'value_error'] for error in errors]))

    def test_transactionschema_invalid_sender_recipient_amount_types(self):
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

    def test_transactionschema_invalid_uuid_output_input_values(self):
        invalid_arguments_values = {
            'uuid': -10,
            'output': {},
            'input': {}
        }
        with self.assertRaises(ValidationError) as err:
            TransactionSchema(**invalid_arguments_values)
            errors = json.loads(err.json())
            self.assertEqual(len(errors), len(invalid_arguments_values.keys()))
            self.assertTrue(all([error.get('type') ==  'value_error' for error in errors]))

    def test_transactionschema_invalid_sender_recipient_amount_values(self):
        invalid_arguments_values = {
            'sender': self.wallet,
            'recipient': 'r3c1p13n7',
            'amount': self.wallet.balance - self._generate_float()
        }
        with self.assertRaises(ValidationError) as err:
            TransactionSchema(**invalid_arguments_values)
            errors = json.loads(err.json())
            self.assertEqual(len(errors), len(invalid_arguments_values.keys()))
            self.assertTrue(all([error.get('type') ==  'value_error' for error in errors]))
