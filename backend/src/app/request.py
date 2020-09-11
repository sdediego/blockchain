# encoding: utf-8

import uuid

from fastapi import Request as BaseRequest
from starlette.datastructure import Headers


class Request(BaseRequest):

    @property
    def headers(self) -> Headers:
        if not hasattr(self, '_headers'):
            request_id = uuid.uuid4().hex.encode('latin-1')
            self.scope['headers'].append((b'X-Request-ID', request_id))
            self._headers = Headers(scope=self.scope)
        return self._headers
