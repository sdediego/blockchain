# encoding: utf-8

import json
import random
from unittest.mock import patch

from pydantic import ValidationError

from src.blockchain.schemas.blockchain import BlockchainSchema
from tests.blockchain.utilities import BlockMixin


class BlockchainSchemaTest(BlockchainMixin):

    def setUp(self):
        super(BlockchainSchemaTest, self).setUp()
        self.chain_length = random.randint(5, 10)
        self.valid_chain = self._generate_valid_chain(self.chain_length)
        self.invalid_chain = self._generate_invalid_chain()

    def test_blockchainschema_valid_chain(self):
        blockchainschema = BlockchainSchema(chain=self.valid_chain)
        self.assertIsInstance(blockchainschema, BlockchainSchema)
        self.assertIsInstance(blockchainschema.chain, list)
        self.assertEqual(len(blockchainschema.chain), self.chain_length)

    def test_blockchainschema_invalid_chain_type(self):
        with self.assertRaises(ValidationError) as err:
            BlockchainSchema(chain={})
            error = json.loads(err.json())[0]
            self.asserEqual(len(errors), 1)
            self.assertEqual(error.get('type'), 'type_error')

    def test_blockchainschema_invalid_chain_value(self):
        with self.assertRaises(ValueError) as err:
            BlockchainSchema(chain=self.invalid_chain)
            error = json.loads(err.json())[0]
            self.assertEqual(error.get('type'), 'value_error')
