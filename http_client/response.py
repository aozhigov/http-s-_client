import re

from http_client.request import Request

re_code = r' [\d]* '
re_protocol = r'[\d\.\d]* '
re_header = r'(?P<header>[a-zA-Z-]*): (?P<value>[0-9\s\w,.;=/:-]*)'
re_charset = r'[a-zA-z/]*; charset=(?P<charset>[\w\d-]*)'
for i in {re_code, re_protocol, re_header, re_charset}:
    re.compile(i)

DECODING = 'ISO-8859-1'


class Response:
    def __init__(self, message: str,
                 code: int,
                 protocol,
                 headers: dict,
                 request,
                 charset: str = '',
                 raw_response: str = ''):
        self._message = message
        self._charset = charset
        self._code = code
        self._protocol = protocol
        self._headers = headers
        self._request = request
        self._raw_response = raw_response

    @classmethod
    def from_bytes(cls, data: bytes,
                   req: Request) -> 'Response':
        response = data.decode(DECODING)
        lines = response.split('\r\n\r\n')
        re_headers = lines[0]

        code = cls.re_search(re_code, response)
        protocol = cls.re_search(re_protocol, response)
        headers = cls.parse_headers(
            re_headers.split('\r\n'))

        return cls(message=lines[1],
                   code=int(code),
                   protocol=float(protocol),
                   headers=headers,
                   request=req,
                   raw_response=response)

    @staticmethod
    def re_search(regular_expressions, response):
        return re.search(regular_expressions,
                         response).group(0)

    @classmethod
    def parse_headers(cls, lines):
        headers = {}
        for line in lines:
            header = re.search(re_header, line)
            if header:
                headers[header.group('header')] = header.group('value')

        return headers

    @property
    def message(self):
        return self._message

    @property
    def charset(self):
        if self._charset == '':
            if 'Content-Type' in self._headers.keys():
                f = re.search(re_charset, self._headers['Content-Type'])
                self._charset = f.group('charset') \
                    if f is not None \
                    else 'utf-8'
        return self._charset

    @property
    def code(self):
        return self._code

    @property
    def location(self):
        if 'Location' in self._headers.keys():
            return self._headers['Location']
        return ''

    @property
    def protocol(self):
        return self._protocol

    @property
    def headers(self):
        return self._headers

    @property
    def request(self):
        return self._request

    @property
    def raw_response(self):
        return self._raw_response
