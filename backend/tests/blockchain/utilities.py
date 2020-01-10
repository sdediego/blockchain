# encoding: utf-8

import random
from unittest import TestCase
from unittest.mock import patch

from src.blockchain.models.block import Block


class BlockMixin(TestCase):

    def _get_genesis_block(self):
        return Block.genesis()

    @patch.object(Block, '_is_valid_schema')
    def _generate_block(self, block: Block, mock_is_valid_schema):
        mock_is_valid_schema.return_value = True
        testing_data = [random.randint(0, 100) for _ in range(10)]
        return Block.mine_block(block, testing_data)
