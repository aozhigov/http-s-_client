import re

from client.request import Request

re_code = r' [\d]* '
re_protocol = r'[\d\.\d]* '
re_header = r'(?P<header>[a-zA-Z-]*): (?P<value>[0-9\s\w,.;=/:-]*)'
re_charset = r'[a-zA-z/]*; charset=(?P<charset>[\w\d-]*)'
for i in {re_code, re_protocol, re_header, re_charset}:
    re.compile(i)

DECODING = 'ISO-8859-1'


class Response:
    def __init__(self, message: str,
                 charset: str,
                 code: int,
                 location: str,
                 protocol,
                 headers: dict,
                 request):
        self._message = message
        self._charset = charset
        self._code = code
        self._location = location
        self._protocol = protocol
        self._headers = headers
        self._request = request

    @classmethod
    def from_bytes(cls, data: bytes,
                   req: Request) -> 'Response':
        response = data.decode(DECODING)
        code = (re.search(re_code, response)).group(0)
        protocol = (re.search(re_protocol, response)).group(0)
        message = response.split('\r\n\r\n')[1]
        charset = ''
        headers = {}
        location = ''

        for item in response.split('\r\n\r\n')[0].split('\r\n'):
            s = re.search(re_header, item)

            if s is not None:
                headers[s.group('header')] = s.group('value')
                if s.group('header') == 'Content-Type' \
                        or s.group('header') == 'content-type':
                    f = re.search(re_charset, s.group('value'))
                    if f is not None:
                        charset = f.group('charset')
                    else:
                        charset = 'utf-8'

                if s.group('header') == 'Location' \
                        or s.group('header') == 'location':
                    location = s.group('value')

        return cls(message=message,
                   charset=charset,
                   code=int(code),
                   location=location,
                   protocol=float(protocol),
                   headers=headers,
                   request=req)

    @property
    def message(self):
        return self._message

    @property
    def charset(self):
        return self._charset

    @property
    def code(self):
        return self._code

    @property
    def location(self):
        return self._location

    @property
    def protocol(self):
        return self._protocol

    @property
    def headers(self):
        return self._headers

    @property
    def request(self):
        return self._request
