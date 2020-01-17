# encoding: utf-8

from fastapi import FastAPI

from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

# Custom logger for api module
fileConfig(join(dirname(dirname(__file__)), 'config', 'logging.cfg'))
logger = getLogger(__name__)


app = FastAPI(__name__)

@app.get("/")
async def root():
    return "Blockchain app is running"
