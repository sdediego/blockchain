# encoding: utf-8

from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

from fastapi import APIRouter, FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.app.middlewares import RequestIDMiddleware, RequestLogMiddleware
from src.app.p2p_server import P2PServer
from src.app.route import APIRoute
from src.blockchain.models.blockchain import Blockchain
from src.client.models.transaction import Transaction
from src.client.models.transactions_pool import TransactionsPool
from src.client.models.wallet import Wallet
from src.config.settings import CORS_MIDDLEWARE_PARAMS

# Custom logger for api module
fileConfig(join(dirname(dirname(__file__)), 'config', 'logging.cfg'))
logger = getLogger(__name__)


app = FastAPI()
router = APIRouter(route_class=APIRoute)

app.add_middleware(CORSMiddleware, **CORS_MIDDLEWARE_PARAMS)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RequestLogMiddleware)

app.blockchain = Blockchain()
app.wallet = Wallet(app.blockchain)
app.transactions_pool = TransactionsPool()
app.p2p_server = P2PServer(app.blockchain, app.transactions_pool)

@router.get('/')
async def root():
    logger.info('[API] GET root.')
    return "Blockchain app is running"

@router.get('/blockchain')
async def blockchain():
    logger.info('[API] GET blockchain.')
    return {'blockchain': app.blockchain}

@router.get('/mine')
async def mine_block():
    logger.info('[API] GET mine. Mining block.')
    transaction_reward = Transaction.reward_mining(app.wallet)
    data = app.transactions_pool.data
    data.append(transaction_reward.info)
    block = app.blockchain.add_block(data)
    logger.info(f'[API] GET mine. Block mined: {block}.')
    await app.p2p_server.broadcast_chain()
    app.transactions_pool.clear_pool(app.blockchain)
    return {'block': block}

@router.post('/transact')
async def transact(data: dict):
    logger.info('[API] POST transact. New transaction.')
    recipient = data.get('recipient')
    amount = data.get('amount')
    transaction = app.transactions_pool.get_transaction(app.wallet.address)
    if transaction:
        transaction.update(app.wallet, recipient, amount)
        logger.info(f'[API] POST transact. Transaction updated: {transaction}.')
    else:
        transaction = Transaction.create(sender=app.wallet, recipient=recipient, amount=amount)
        logger.info(f'[API] POST transact. Transaction made: {transaction}.')
    app.transactions_pool.add_transaction(transaction)
    await app.p2p_server.broadcast_transaction(transaction)
    return {'transaction': transaction}

@router.get('/balance')
async def balance():
    logger.info('[API] GET balance. Calculating balance.')
    address = app.wallet.address
    balance = app.wallet.balance
    logger.info(f'[API] GET balance. Address: {address}, balance: {balance}.')
    return {'address': address, 'balance': balance}

@router.get('/addresses')
async def addresses():
    logger.info('[API] GET addresses. Retrieving known addresses.')
    addresses = set()
    for block in app.blockchain.chain:
        for transaction in block.data:
            addresses.update(transaction.get('output').keys())
    return {'addresses': list(addresses)}

@router.get('/transactions')
async def transactions():
    logger.info('[API] GET transactions. Retrieving transactions.')
    transactions = app.transactions_pool.data
    return {'transactions': transactions}

app.include_router(router)
