"""
The MIT License (MIT)
Copyright (c) 2015-present Rapptz
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import json
import os

from typing import Any

try:
    import orjson
except ModuleNotFoundError:
    HAS_ORJSON = False
else:
    HAS_ORJSON = True

if HAS_ORJSON:

    def _to_json(obj: Any) -> str:
        return orjson.dumps(obj).decode('utf-8')


    _from_json = orjson.loads

else:

    def _to_json(obj: Any) -> str:
        return json.dumps(obj, ensure_ascii=True)


    _from_json = json.loads


class Credentials:
    def __init__(self,
                 host: str,
                 password: str,
                 user_id: int,
                 port: int = 2333,
                 is_https: bool = False,
                 resume_key: str = str(os.urandom(8).hex())):
        self._host = host
        self._password = password
        self._port = port
        self._is_https = is_https

        self._headers = {
            "Authorization": password,
            "User-Id": str(user_id),
            "Client-Name": "Lavacord",
            'Resume-Key': resume_key
        }

    @property
    def password(self) -> str:
        return self._password

    @property
    def host(self) -> str:
        return f'{"https://" if self._is_https else "http://"}{self.host}:{self._port}'

    @property
    def websocket_host(self) -> str:
        return self.host if self._is_https else f"ws://{self._host}:{self._port}"

    @property
    def headers(self) -> dict:
        return self._headers
