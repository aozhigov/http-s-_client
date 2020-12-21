import unittest
from pathlib import Path
from unittest.mock import patch

from http_client.client import Client
from http_client.exceptions import ValueRequestTypeException, \
    HTTPSClientException, ConnectException, UnreadableFileException
from http_client.request import Request
from http_client.response import Response


class TestHttpClient(unittest.TestCase):
    def test_check_get_request(self):
        req = Request(protocol='HTTP/1.1',
                      method='GET',
                      timeout=1000,
                      data='',
                      url='http://ptsv2.com/t/lp5td-1586273836/post')
        assert ('GET /t/lp5td-1586273836/post HTTP/1.1\r\n' +
                'Host: ptsv2.com\r\n' +
                'Connection: close\r\n' +
                'Content-Length: 0\r\n\r\n') == str(req)

    def test_check_post_request_text(self):
        req = Request(protocol='HTTP/1.1',
                      method='POST',
                      timeout=1000,
                      data='Hello, World!',
                      url='http://ptsv2.com/t/lp5td-1586273836/post')
        assert ('POST /t/lp5td-1586273836/post HTTP/1.1\r\n' +
                'Host: ptsv2.com\r\n' +
                'Connection: close\r\n' +
                'Content-Length: 13\r\n\r\n' +
                'Hello, World!') == str(req)

    def test_bytes(self):
        req = Request(protocol='HTTP/1.1',
                      method='POST',
                      timeout=1000,
                      data='Hello',
                      url='http://ptsv2.com/t/lp5td-1586273836/post',
                      agent='Mozilla/5.0')
        e = str(req)
        b = bytes(req).decode('ISO-8859-1')
        assert b == e

    def test_check_post_request_from_file(self):
        path = Path.cwd() / 'tests' / 'resources' / 'test_text.txt'
        with path.open('w+') as f:
            f.write('abracadabra')
        assert 'abracadabra' == Request.prepare_data(data=str(path))

    def test_response(self):
        text = 'HTTP/1.1 200 Ok\r\n' \
               'Server: VK\r\n' \
               'Connection: close\r\n' \
               'Content-Type: text/html; charset=UTF-8\r\n\r\nHello'
        new_response = Response.from_bytes(
            text.encode('utf-8'), None)
        assert 200 == new_response.code
        assert ({'Server': 'VK',
                 'Connection': 'close',
                 'Content-Type': 'text/html; charset=UTF-8'} ==
                new_response.headers)
        assert 'UTF-8' == new_response.charset
        assert 'Hello' == new_response.message

    def test_prepare_headers(self):
        path = Path.cwd() / 'tests' / 'resources' / 'cookie.txt'
        with path.open('w') as f:
            f.write('hello')

        req = Request(method='GET',
                      agent='Chrome',
                      cookie_file=str(path),
                      cookie='income=1',
                      reference='https://vk.com/',
                      headers=['Content-Length: 30',
                               'Pory: tau'],
                      url='http://ptsv2.com/t/lp5td-1586273836/post',
                      data='')
        assert {'Content-Length': '30',
                'Pory': 'tau', 'Reference': 'https://vk.com/',
                'Cookie': 'hello', 'User-Agent': 'Chrome',
                'Host': 'ptsv2.com', 'Connection': 'close'} == req.headers

    @patch('http_client.client.Client')
    def test_request_http(self, mock_request):
        client_mock = mock_request()
        client_mock.do_request.return_value = \
            Response(message='Thank you for this dump. '
                             'I hope you have a lovely day!',
                     charset='', code=200, protocol='',
                     headers=dict(), request=None)
        req = Request(protocol='HTTP/1.1',
                      method='GET',
                      timeout=1000,
                      data='',
                      url='http://ptsv2.com/t/lp5td-1586273836/post')
        data = client_mock.do_request(req)
        assert data is not None
        assert data.message == 'Thank you for this dump. ' \
                               'I hope you have a lovely day!'

    @patch('http_client.client.Client')
    def test_request_https(self, mock_request):
        client_mock = mock_request()
        client_mock.do_request.return_value = \
            Response(code=200,
                     message='<!DOCTYPE html>', charset='',
                     protocol='', headers=dict(), request=None)
        req = Request(protocol='HTTP/1.1',
                      method='GET',
                      timeout=1000,
                      data='',
                      url='https://habr.com/ru/')
        data = client_mock.do_request(req)
        assert data is not None
        assert data.code == 200
        assert data.message.__contains__('<!DOCTYPE html>')

    def test_prepare_data(self):
        f = Request.prepare_data
        assert 'test' == f(data='test')
        assert f(data=None) == ''
        assert '' == f('')
        assert 'hello' == f('tests/resources/cookie.txt')

    def test_exceptions(self):
        self.assertRaises(ValueRequestTypeException,
                          Request,
                          protocol='HTTP/1.1',
                          method='HHHHEEE',
                          timeout=1000,
                          data='',
                          url='https://habr.com/ru/')
        self.assertRaises(HTTPSClientException,
                          Request,
                          protocol='HTTP/1.1',
                          method='GET',
                          timeout=1000,
                          data='',
                          url='https://habr.com/ru/',
                          cookie_file='sdzc.txt')
        client = Client(10)
        req = Request(protocol='HTTP/1.1',
                      method='GET',
                      timeout=1000,
                      data='',
                      url='httff://habrweerwd.erff/ru/')
        self.assertRaises(ConnectException, client.do_request, req)
        self.assertRaises(UnreadableFileException,
                          Request,
                          protocol='HTTP/1.1',
                          method='GET',
                          timeout=1000,
                          data='',
                          url='https://habr.com/ru/',
                          cookie_file=str(Path.cwd()))

    @patch('http_client.client.Client')
    def test_redirect(self, mock_request):
        client_mock = mock_request()
        client_mock.do_request.return_value = \
            Response(message='<!DOCTYPE html>',
                     code=200, protocol='', charset='utf-8',
                     headers=dict(), request=None)
        req = Request(protocol='HTTP/1.1',
                      method='GET',
                      timeout=1000,
                      data='',
                      url='https://vk.com/feed')
        client = Client(10)
        data = client_mock.do_request(req)
        assert data is not None
        assert data.code == 200
        assert data.message.__contains__('<!DOCTYPE html>')
        assert data.charset.lower() == 'utf-8'

        client.max_hops = 0
        self.assertRaises(ConnectException,
                          client.do_request, req)


if __name__ == '__main__':
    unittest.main()
