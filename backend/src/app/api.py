# encoding: utf-8

from fastapi import FastAPI

from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

from src.blockchain.models.block import Block
from src.blockchain.models.blockchain import Blockchain

# Custom logger for api module
fileConfig(join(dirname(dirname(__file__)), 'config', 'logging.cfg'))
logger = getLogger(__name__)


app = FastAPI(__name__)

chain = [Block.genesis()]
app.blockchain = Blockchain(chain)

@app.get('/')
async def root():
    logger.info('[API] GET root.')
    return "Blockchain app is running"

@app.get('/blockchain')
async def blockchain():
    logger.info('[API] GET blockchain.')
    return {'blockchain': app.blockchain}

@app.get('/mine')
async def mine_block():
    data = ['test data']
    logger.info('[API] GET mine. Mining new block.')
    app.blockchain.add_block(data)
    new_block = app.blockchain.last_block
    logger.info(f'[API] GET mine. New block mined: {new_block}')
    return {'new_block': new_block}
