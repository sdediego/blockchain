# encoding: utf-8

from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

from src.app.routing import APIRoute, APIRouter
from src.client.models.transaction import Transaction

# Custom logger for controllers module
fileConfig(join(dirname(dirname(__file__)), 'config', 'logging.cfg'))
logger = getLogger(__name__)


router = APIRouter(route_class=APIRoute)

@router.get('/')
async def root():
    logger.info('[API] GET root.')
    return "Blockchain app is running"

@router.get('/blockchain')
async def blockchain():
    logger.info('[API] GET blockchain.')
    return {'blockchain': router.blockchain}

@router.get('/mine')
async def mine_block():
    logger.info('[API] GET mine. Mining block.')
    transaction_reward = Transaction.reward_mining(router.wallet)
    data = router.transactions_pool.data
    data.append(transaction_reward.info)
    block = router.blockchain.add_block(data)
    logger.info(f'[API] GET mine. Block mined: {block}.')
    await router.p2p_server.broadcast_chain()
    router.transactions_pool.clear_pool(router.blockchain)
    return {'block': block}

@router.post('/transact')
async def transact(data: dict):
    logger.info('[API] POST transact. New transaction.')
    recipient = data.get('recipient')
    amount = data.get('amount')
    transaction = router.transactions_pool.get_transaction(router.wallet.address)
    if transaction:
        transaction.update(router.wallet, recipient, amount)
        logger.info(f'[API] POST transact. Transaction updated: {transaction}.')
    else:
        transaction = Transaction.create(sender=router.wallet, recipient=recipient, amount=amount)
        logger.info(f'[API] POST transact. Transaction made: {transaction}.')
    router.transactions_pool.add_transaction(transaction)
    await router.p2p_server.broadcast_transaction(transaction)
    return {'transaction': transaction}

@router.get('/balance')
async def balance():
    logger.info('[API] GET balance. Calculating balance.')
    address = router.wallet.address
    balance = router.wallet.balance
    logger.info(f'[API] GET balance. Address: {address}, balance: {balance}.')
    return {'address': address, 'balance': balance}

@router.get('/addresses')
async def addresses():
    logger.info('[API] GET addresses. Retrieving known addresses.')
    addresses = set()
    for block in router.blockchain.chain:
        for transaction in block.data:
            addresses.update(transaction.get('output').keys())
    return {'addresses': list(addresses)}

@router.get('/transactions')
async def transactions():
    logger.info('[API] GET transactions. Retrieving transactions.')
    transactions = router.transactions_pool.data
    return {'transactions': transactions}
