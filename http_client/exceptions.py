class HTTPSClientException(Exception):
    def __init__(self, message: str):
        self.message = message


class DataFromFileAndFromStringException(HTTPSClientException):
    def __init__(self):
        super().__init__('You can\'t send data from a file '
                         'and from a string at the same time')


class UnreadableFileException(HTTPSClientException):
    def __init__(self, name_file: str):
        super().__init__(f'Unable to read the file {name_file}')


class VerboseException(HTTPSClientException):
    def __init__(self):
        super().__init__('The -v key can`t be combined with -1 or -0 keys')


class ConnectException(HTTPSClientException):
    def __init__(self, link: str):
        super().__init__(f'not connect to the server, check URL {link}')


class ValueRequestTypeException(HTTPSClientException):
    def __init__(self, request_type: str):
        super().__init__(f'{request_type} the request type does '
                         f'not exist. See help')
