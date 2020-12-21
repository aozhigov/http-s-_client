from pathlib import Path

from yarl import URL

from http_client.exceptions import (UnreadableFileException,
                                    HTTPSClientException)
from http_client.method import Method

ENCODING = 'ISO-8859-1'


class Request:
    def __init__(self,
                 url: str,
                 method: str = None,
                 headers: list = None,
                 timeout: float = None,
                 reference: str = None,
                 cookie: str = None,
                 agent: str = None,
                 cookie_file: str = None,
                 protocol: str = None,
                 data: str = None):
        self._data = self.prepare_data(data)
        self._protocol = protocol
        self._reference = reference
        self._agent = agent
        self._cookie = cookie
        self._cookie_file = cookie_file
        self._timeout = timeout
        self._url = URL(url)
        self._method = Method.check_request_type(method)
        self._headers = {}
        self._prepare_headers(headers)

    def _prepare_headers(self, headers: list):
        self.parse_console_headers(headers)

        self.set_value_in_headers('Reference', self._reference)
        self.set_value_in_headers('Cookie', self._cookie)
        self.set_value_in_headers('User-Agent', self._agent)
        self.set_value_in_headers('Host', self.url.host)
        self.set_value_in_headers('Connection', 'close')

        self.add_cookie_from_file()

    def add_cookie_from_file(self):
        if self._cookie_file:
            if Path(self._cookie_file).exists():
                try:
                    with open(self._cookie_file, 'r') as f:
                        self.headers['Cookie'] = f.read()
                except Exception as e:
                    raise UnreadableFileException(str(e))
            else:
                raise HTTPSClientException(self._cookie_file)

    def parse_console_headers(self, headers):
        if headers:
            for header in headers:
                separator_ind = header.find(':')
                value = header[separator_ind + 1:].strip()
                self._headers[header[0:separator_ind]] = value

    def set_value_in_headers(self, headers: str, value):
        if value:
            self._headers[headers] = value

    def __repr__(self) -> str:
        return bytes(self).decode(ENCODING)

    def __bytes__(self):
        result = bytearray(f'{self._method.name} {self.url.path} '
                           f'{self._protocol}\r\n', ENCODING)
        for header, value in self.headers.items():
            result += bytes(f'{header}: {value}\r\n', ENCODING)

        result += bytes(f'Content-Length: {len(self._data)}\r\n',
                        ENCODING)
        result += bytes(f'\r\n{self._data}', ENCODING)

        return bytes(result)

    @staticmethod
    def prepare_data(data: str = None):
        result_data = ''
        if data:
            result_data = data

        if data is not None and data != '' and Path(data).exists():
            try:
                with open(data, 'r') as f:
                    result_data = f.read()
            except Exception:
                raise UnreadableFileException(data)

        return result_data

    @property
    def request_method(self):
        return self._method.name

    @request_method.setter
    def request_method(self, value: str):
        self._method = Method.check_request_type(value)

    @property
    def url(self) -> URL:
        return self._url

    @url.setter
    def url(self, value: str):
        self._url = URL(value)

    @url.setter
    def url(self, value: URL):
        self._url = value

    @property
    def cookie(self):
        return self._cookie

    @cookie.setter
    def cookie(self, value: str):
        self._cookie = value
        self._prepare_headers([])

    @property
    def cookie_file(self):
        return self._cookie_file

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value: float):
        self._timeout = value

    @property
    def user_agent(self):
        return self._agent

    @user_agent.setter
    def user_agent(self, value):
        self._agent = value
        self._prepare_headers([])

    @property
    def headers(self):
        return self._headers

    @property
    def reference(self):
        return self._reference

    @property
    def data(self):
        return self._data

    @property
    def protocol(self):
        return self._protocol
