# encoding: utf-8

import json
from unittest.mock import patch

from pydantic import ValidationError

from src.blockchain.schemas.block import BlockSchema
from tests.unit.blockchain.utilities import BlockMixin


class BlockSchemaTest(BlockMixin):

    def setUp(self):
        super(BlockSchemaTest, self).setUp()
        self.block = self._generate_valid_block()
        self.valid_arguments = self.block.info
        self.invalid_arguments_types = {
            'index': '1nd3x',
            'timestamp': 't1m357amp',
            'nonce': 'n0nc3',
            'difficulty': 'd1ff1cul7y',
            'data': 'da7a',
            'last_hash': 1001001010111001,
            'hash': 1111001010001001
        }
        self.invalid_arguments_values = {
            'index': -1,
            'timestamp': 31416,
            'nonce': -1,
            'difficulty': 0,
            'data': [],
            'last_hash': 'la57_ha5h',
            'hash': 'ha5h'
        }

    def _generate_valid_block(self):
        genesis_block = self._get_genesis_block()
        block = self._generate_block(genesis_block)
        return self._generate_block(block)

    def test_blockschema_valid_arguments_types(self):
        blockschema = BlockSchema(**self.valid_arguments)
        self.assertIsInstance(blockschema, BlockSchema)
        self.assertIsInstance(blockschema.index, int)
        self.assertIsInstance(blockschema.timestamp, int)
        self.assertIsInstance(blockschema.nonce, int)
        self.assertIsInstance(blockschema.difficulty, int)
        self.assertIsInstance(blockschema.data, list)
        self.assertIsInstance(blockschema.last_hash, str)
        self.assertIsInstance(blockschema.hash, str)

    def test_blockschema_invalid_arguments_types(self):
        with self.assertRaises(ValidationError) as err:
            BlockSchema(**self.invalid_arguments_types)
            errors = json.loads(err.json())
            self.asserEqual(len(errors), len(self.invalid_arguments_types.keys()))
            self.assertTrue(all([error.get('type') in ['type_error', 'value_error'] for error in errors]))

    def test_blockchain_invalid_arguments_values(self):
        with self.assertRaises(ValidationError) as err:
            BlockSchema(**self.invalid_arguments_values)
            errors = json.loads(err.json())
            self.asserEqual(len(errors), len(self.invalid_arguments_values.keys()))
            self.assertTrue(all([error.get('type') == 'value_error' for error in errors]))
