# encoding: utf-8

import random
from unittest.mock import Mock, patch

from src.blockchain.models.block import Block
from src.blockchain.models.blockchain import Blockchain
from src.exceptions import BlockchainError
from tests.blockchain.utilities import BlockchainMixin


class BlockchainTest(BlockchainMixin):

    def setUp(self):
        super(BlockchainTest, self).setUp()
        self.chain_length = random.randint(5, 10)
        self.valid_chain = self._generate_valid_chain(self.chain_length)
        self.invalid_chain = self._generate_invalid_chain()
        self.blockchain = Blockchain(self.valid_chain)
        self.serialized = self.blockchain.serialize()

    def test_blockchain_string_representation(self):
        blockchain_str = str(self.blockchain)
        self.assertIn('Blockchain', blockchain_str)
        self.assertIn('Block', blockchain_str)
        self.assertTrue(all([f'index: {index}' in blockchain_str for index in range(self.chain_length)]))

    def test_blockchain_genesis_property(self):
        self.assertTrue(self.blockchain.genesis == self._get_genesis_block())

    @patch.object(Block, 'mine_block')
    def test_blockchain_last_block_property(self, mock_mine_block):
        last_block = self.blockchain.last_block
        new_block = self._generate_block(last_block)
        mock_mine_block.return_value = new_block
        self.assertTrue(last_block == self.blockchain.chain[-1])
        self.blockchain.add_block(new_block.data)
        self.assertFalse(last_block == self.blockchain.last_block)

    @patch.object(Block, 'mine_block')
    def test_blockchain_length_property(self, mock_mine_block):
        last_block = self.blockchain.last_block
        new_block = self._generate_block(last_block)
        mock_mine_block.return_value = new_block
        self.assertEqual(self.blockchain.length, self.chain_length)
        self.blockchain.add_block(new_block.data)
        self.assertNotEqual(self.blockchain.length, self.chain_length)

    def test_blockchain_serialization(self):
        self.assertIsInstance(self.serialized, list)
        self.assertTrue(all([isinstance(block, str) for block in self.serialized]))

    def test_blockchain_deserialization(self):
        deserialized = Blockchain.deserialize(self.serialized)
        self.assertIsInstance(deserialized, Blockchain)
        self.assertTrue(hasattr(deserialized, 'chain'))
        for block_one, block_two in zip(deserialized.chain, self.blockchain.chain):
            self.assertTrue(block_one == block_two)

    @patch.object(Blockchain, '_is_valid_schema')
    def test_blockchain_create_valid_schema(self, mock_is_valid_schema):
        mock_is_valid_schema.return_value = True
        blockchain = Blockchain.create(self.valid_chain)
        self.assertTrue(mock_is_valid_schema.called)
        self.assertIsInstance(blockchain, Blockchain)
        self.assertEqual(blockchain.chain, self.valid_chain)

    @patch.object(Blockchain, '_is_valid_schema')
    def test_blockchain_create_invalid_schema(self, mock_is_valid_schema):
        err_message = '[Blockchain] Validation error.'
        mock_is_valid_schema.side_effect = Mock(side_effect=BlockchainError(err_message))
        with self.assertRaises(BlockchainError) as err:
            Blockchain.create(self.invalid_chain)
            self.assertTrue(mock_is_valid_schema.called)
            self.assertIsInstance(err, BlockchainError)
            self.assertIn(err_message, err.message)

    @patch.object(Block, 'mine_block')
    def test_add_block(self, mock_mine_block):
        last_block = self.blockchain.last_block
        new_block = self._generate_block(last_block)
        mock_mine_block.return_value = new_block
        self.blockchain.add_block(new_block.data)
        self.assertEqual(self.blockchain.length, self.chain_length + 1)
        self.assertFalse(self.blockchain.last_block == last_block)

    def test_blockchain_is_valid_schema_valid(self):
        Blockchain.is_valid(self.valid_chain)

    def test_blockchain_is_valid_schema_invalid(self):
        err_message = '[Blockchain] Validation error.'
        with self.assertRaises(BlockchainError) as err:
            Blockchain.is_valid(self.invalid_chain)
            self.assertIsInstance(err, BlockchainError)
            self.assertIn(err_message, err.message)
