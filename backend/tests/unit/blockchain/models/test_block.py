# encoding: utf-8

from unittest.mock import Mock, patch

from src.blockchain.models.block import Block
from src.blockchain.models.utils import get_utcnow_timestamp
from src.exceptions import BlockError
from tests.unit.blockchain.utilities import BlockMixin


class BlockTest(BlockMixin):

    def setUp(self):
        super(BlockTest, self).setUp()
        self.genesis_block = self._get_genesis_block()
        self.first_block = self._generate_block(self.genesis_block)
        self.second_block = self._generate_block(self.first_block)
        self.block_info = self.second_block.info
    
    def test_block_string_representation(self):
        self.assertTrue(all([attr in str(self.first_block) for attr in self.block_info.keys()]))

    def test_block_equal_same_block(self):
        self.assertTrue(self.first_block == self.first_block)
    
    def test_block_equal_different_block(self):
        self.assertTrue(self.first_block != self.second_block)

    def test_block_info_property(self):
        attributes = self.first_block.__dict__
        for attribute in attributes:
            self.assertIn(attribute, self.first_block.info)

    def test_block_serialization(self):
        self.assertIsInstance(self.first_block.serialize(), str)

    def test_block_deserialization(self):
        block = self.first_block.serialize()
        self.assertIsInstance(Block.deserialize(block), Block)

    @patch.object(Block, 'is_valid_schema')
    def test_block_create_valid_schema(self, mock_is_valid_schema):
        mock_is_valid_schema.return_value = True
        block = Block.create(**self.block_info)
        self.assertTrue(mock_is_valid_schema.called)
        self.assertIsInstance(block, Block)
        self.assertTrue(all([attr in block.info.keys() for attr in self.block_info.keys()]))
        self.assertTrue(all([value in block.info.values() for value in self.block_info.values()]))

    @patch.object(Block, 'is_valid_schema')
    def test_block_create_invalid_schema(self, mock_is_valid_schema):
        err_message = 'Validation error'
        mock_is_valid_schema.side_effect = Mock(side_effect=BlockError(err_message))
        with self.assertRaises(BlockError) as err:
            Block.create(**self.block_info)
            self.assertTrue(mock_is_valid_schema.called)
            self.assertIsInstance(err, BlockError)
            self.assertIn(err_message, err.message)

    def test_block_genesis(self):
        attributes = vars(self.first_block).keys()
        self.assertIsInstance(self.genesis_block, Block)
        for attribute in self.genesis_block.info.keys():
            self.assertIn(attribute, attributes)

    @patch.object(Block, 'is_valid_schema')
    @patch.object(Block, 'proof_of_work')
    def test_block_mine_block(self, mock_proof_of_work, mock_is_valid_schema):
        mock_is_valid_schema.return_value = True
        mock_proof_of_work.return_value = self.block_info
        block = Block.mine_block(self.first_block, self.second_block.data)
        self.assertTrue(mock_is_valid_schema.called)
        self.assertTrue(mock_proof_of_work.called)
        self.assertIsInstance(block, Block)

    @patch.object(Block, 'is_valid_schema')
    @patch.object(Block, 'adjust_difficulty')
    def test_block_proof_of_work(self, mock_adjust_difficulty, mock_is_valid_schema):
        mock_is_valid_schema.return_value = True
        mock_adjust_difficulty.return_value = self.first_block.difficulty + 1
        block = Block.mine_block(self.first_block, self.second_block.data)
        self.assertTrue(mock_is_valid_schema.called)
        self.assertTrue(mock_adjust_difficulty.called)
        self.assertIsInstance(block, Block)

    def test_block_adjust_difficulty_increase(self):
        self.second_block.timestamp = 10
        difficulty = Block.adjust_difficulty(self.second_block, 1)
        self.assertEqual(difficulty, self.second_block.difficulty + 1)

    def test_block_adjust_difficulty_decrease(self):
        self.second_block.timestamp = 10
        difficulty = Block.adjust_difficulty(self.second_block, get_utcnow_timestamp())
        self.assertEqual(difficulty, self.second_block.difficulty - 1)

    def test_block_adjust_difficulty_set_to_one(self):
        self.second_block.timestamp = 1
        difficulty = Block.adjust_difficulty(self.second_block, get_utcnow_timestamp())
        self.assertEqual(difficulty, 1)

    def test_block_is_valid(self):
        Block.is_valid(self.first_block, self.second_block)

    def test_block_is_valid_schema_validation_error(self):
        self.second_block.hash = '1nval1d ha57'
        with self.assertRaises(BlockError) as err:
            Block.is_valid(self.first_block, self.second_block)
            self.assertIsInstance(err, BlockError)
            self.assertIn('Validation error', err.message)

    def test_block_is_valid_hashes_validation_error(self):
        self.first_block.hash = '1nval1d ha57'
        err_message = (f'Block {self.first_block.index} hash "{self.first_block.hash}" and '
                       f'block {self.second_block.index} last_hash "{self.second_block.last_hash}" must match.')
        with self.assertRaises(BlockError) as err:
            Block.is_valid(self.first_block, self.second_block)
            self.assertIn(err_message, err.message)

    def test_block_is_valid_difficulty_validation_error(self):
        self.first_block.difficulty = 10
        err_message = ('Difficulty must differ as much by 1 between blocks: '
                      f'block {self.second_block.index} difficulty: {self.second_block.difficulty}, '
                      f'block {self.first_block.index} difficulty: {self.first_block.difficulty}.')
        with self.assertRaises(BlockError) as err:
            Block.is_valid(self.first_block, self.second_block)
            self.assertIn(err_message, err.message)
