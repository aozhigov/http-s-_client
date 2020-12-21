import ssl
from socket import socket, AF_INET, SOCK_STREAM

from http_client.exceptions import ConnectException
from http_client.request import Request
from http_client.response import Response

CHUNK = 1024


class Client:
    def __init__(self, max_hops: int):
        self._const_max_hops = max_hops
        self._max_hops = max_hops
        self._response = None

    def get_response(self, request):
        return Response.from_bytes(
            self._get_response(self._prepare_socket(request), request),
            request)

    @staticmethod
    def _get_response(sock, request: Request):
        response = bytearray()
        try:
            sock.connect((
                request.url.host,
                request.url.port))

            if request.url.scheme == 'https':
                sock.do_handshake()

            sock.sendall(bytes(request))

        except Exception:
            raise ConnectException(f'{request.url.host}: '
                                   f'{request.url.port}')

        while True:
            data = sock.recv(CHUNK)
            if not data or data == '':
                break
            response.extend(data)

        sock.close()
        return response

    def do_request(self, request: Request):
        self._max_hops = self._const_max_hops
        self._response = self.get_response(request)

        while ((300 <= self._response.code < 400 or
                self._response.location != '') and self.max_hops):
            temp_request = Request(url=self._response.location,
                                   reference=request.reference,
                                   cookie=request.cookie,
                                   agent=request.user_agent,
                                   headers=request.headers,
                                   method=request.request_method,
                                   cookie_file=request.cookie_file,
                                   timeout=request.timeout,
                                   data=request.data,
                                   protocol=request.protocol)
            self._response = self.get_response(temp_request)
            self._max_hops -= 1

        if (not self.max_hops or 300 <= self._response.code < 400 or
                self._response.location != ''):
            raise ConnectException(str(request.url))

        return self._response

    @staticmethod
    def _prepare_socket(request: Request):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.settimeout(request.timeout)

        if request.url.scheme == 'https':
            sock = ssl.wrap_socket(sock)

        return sock

    @property
    def max_hops(self):
        return self._max_hops

    @max_hops.setter
    def max_hops(self, value: int):
        self._max_hops = value
        self._const_max_hops = value
