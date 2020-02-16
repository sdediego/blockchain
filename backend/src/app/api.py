# encoding: utf-8

from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

from fastapi import FastAPI

from src.app.p2p_server import P2PServer
from src.blockchain.models.blockchain import Blockchain
from src.client.models.transaction import Transaction
from src.client.models.transactions_pool import TransactionsPool
from src.client.models.wallet import Wallet

# Custom logger for api module
fileConfig(join(dirname(dirname(__file__)), 'config', 'logging.cfg'))
logger = getLogger(__name__)


app = FastAPI(__name__)

app.blockchain = Blockchain()
app.wallet = Wallet(app.blockchain)
app.transactions_pool = TransactionsPool()
app.p2p_server = P2PServer(app.blockchain, app.transactions_pool)

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
    logger.info('[API] GET mine. Mining block.')
    data = app.transactions_pool.data
    app.blockchain.add_block(data)
    block = app.blockchain.last_block
    logger.info(f'[API] GET mine. Block mined: {block}.')
    await app.p2p_server.broadcast_chain()
    app.transactions_pool.clear_pool(app.blockchain)
    return {'block': block}

@app.post('/transact')
async def transact(data: dict):
    recipient = data.get('recipient')
    amount = data.get('amount')
    transaction = app.transactions_pool.get_transaction(app.wallet.address)
    if transaction:
        transaction.update(app.wallet, recipient, amount)
        logger.info(f'[API] POST transact. Transaction updated: {transaction}.')
    else:
        transaction = Transaction(sender=app.wallet, recipient=recipient, amount=amount)  # create
        logger.info(f'[API] POST transact. Transaction made: {transaction}.')
    await app.p2p_server.broadcast_transaction(transaction)
    return {'transaction': transaction}
