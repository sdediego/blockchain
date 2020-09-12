# encoding: utf-8

from typing import Callable

from fastapi import Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute as BaseAPIRoute

from src.app.request import Request


class APIRoute(BaseAPIRoute):
    """
    API Route for handling request validation errors.

    In case of unprocessable request a custom json response
    is sent back with error detail and 422 status code.
    """

    def get_route_handler(self) -> Callable:
        base_route_handler = super(APIRoute, self).get_route_handler()

        async def route_handler(request: Request) -> Response:
            try:
                return await base_route_handler(request)
            except RequestValidationError as err:
                body = await request.body()
                content = jsonable_encoder({'errors': err.errors(), 'body': body.decode()})
                return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return route_handler
