# encoding: utf-8

from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from src.app.middlewares import RequestIDMiddleware, RequestLogMiddleware
from src.app.controllers import router
from src.config.settings import CORS_MIDDLEWARE_PARAMS

# Custom logger for api module
fileConfig(join(dirname(dirname(__file__)), 'config', 'logging.cfg'))
logger = getLogger(__name__)


app = FastAPI()

app.router = router
app.add_middleware(CORSMiddleware, **CORS_MIDDLEWARE_PARAMS)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RequestLogMiddleware)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, err):
    content = jsonable_encoder({'errors': err.errors()})
    return JSONResponse(content=content, status_code=err.status_code)
