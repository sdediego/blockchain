# encoding: utf-8

from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

from pydantic import BaseModel, validator

from src.blockchain.models.block import Block
from src.exceptions import BlockError

# Custom logger for blockchain schema module
fileConfig(join(dirname(dirname(dirname(__file__))), 'config', 'logging.cfg'))
logger = getLogger(__name__)


class BlockchainSchema(BaseModel):
    """
    Schema for definition and validation of blockchain attributes.
    """
    chain: list

    class Config:
        title = 'Blockchain schema'
        validate_all = True

    @validator('chain')
    def valid_chain(cls, value: list):
        """
        Validate chain items values.

        :param list value: provided chain value.
        :return list: validated chain value.
        :raise ValueError: on invalid block in chain.
        """
        genesis = last_block = value[0]
        if not isinstance(genesis, Block) or genesis != Block.genesis():
            message = f'Invalid chain genesis block: {genesis}.'
            logger.error(f'[BlockchainSchema] Validation error. {message}')
            raise ValueError(message)
        for block in value[1:]:
            try:
                assert isinstance(block, Block)
                Block.is_valid(last_block, block)
            except (AssertionError, BlockError) as err:
                message = err.message if hasattr(err, 'message') else f'Invalid block: {block}.'
                logger.error(f'[BlockchainSchema] Validation error. {message}')
                raise ValueError(message)
            last_block = block
        return value
