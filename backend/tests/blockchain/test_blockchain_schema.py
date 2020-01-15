# encoding: utf-8

import json
import random
from unittest.mock import patch

from pydantic import ValidationError

from src.blockchain.schemas.blockchain import BlockchainSchema
from tests.blockchain.utilities import BlockMixin


class BlockchainSchemaTest(BlockMixin):

    def setUp(self):
        super(BlockchainSchemaTest, self).setUp()
        self.chain_length = random.randint(5, 10)
        self.valid_chain = self._generate_valid_chain(self.chain_length)
        self.invalid_chain = self._generate_invalid_chain()

    def _generate_valid_chain(self, length: int):
        chain = [self._get_genesis_block()]
        while len(chain) < length:
            last_block = chain[-1]
            chain.append(self._generate_block(last_block))
        return chain
    
    def _generate_invalid_chain(self):
        chain = self.valid_chain[:]
        block = self._generate_block(random.choice(chain[:-2]))
        block.index = chain[-1].index + 1 
        chain.append(block)
        return chain

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
