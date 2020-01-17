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
    logger.info(f'[API] GET blockchain.')
    response = app.blockchain.serialize()
    return {'blockchain': response}
