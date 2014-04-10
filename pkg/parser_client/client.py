# -*- coding: utf-8 -*-

import json
import requests
from socket import timeout as TimeoutError


__all__ = ['ParserClient', 'send_request', ]


class ParserCompressor(object):
    PARSER_ZLIB = 'zlib'

    __slots__ = ('__compressor_type', '__compressor', )

    def __init__(self, compressor_type=PARSER_ZLIB):
        """
        Initialize instance

        :param string compressor_type: type of compressor engine
        """

        self.__compressor_type = ''
        self.__compressor = None

        self.compressor_type = compressor_type

    @property
    def compressor_type(self):
        """
        :rtype string:
        """
        return self.__compressor_type

    @compressor_type.setter
    def compressor_type(self, c_type):
        """
        :param string c_type: type of compressor
        """
        try:
            self.__compressor = __import__(c_type)
            self.__compressor_type = c_type
        except ImportError:
            pass

    def compress(self, string="", level=5):
        """
        Perform compress

        :param string string: Data to compress
        :param int level: compression level

        :return bytearray:
        """
        if not string:
            return u''

        return self.__compressor.compress(string, level)

    def decompress(self, string=None):
        """
        Perform decompress

        :param bytearray string: Data to decompress

        :return string:
        """

        if not string:
            return u''

        return unicode(self.__compressor.decompress(string))


class ParserClient(object):
    __slots__ = ('__compressor', '__parser_server', '__timeout', )

    def __init__(self, parser_server, compressor_type=ParserCompressor.PARSER_ZLIB, timeout=10):
        """
        Instance of parser client

        :param string parser_server: url of parser
        :param string compressor_type: type of string compressor. @see ParserCompressor
        :param int timeout: connection timeout
        """
        self.__compressor = ParserCompressor(compressor_type)
        self.__parser_server = parser_server
        self.__timeout = int(timeout)

    def process(self, text):
        """
        Perform request to the parser.

        :param string text: text, which need to parse

        :return string;
        """
        data = {
            "action": "parse",
            "html": unicode(text)
        }

        jdata = json.dumps(data)

        cdata = self.__compressor.compress(jdata)
        try:
            result = requests.post(self.__parser_server, cdata, timeout=self.__timeout)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, TimeoutError, ):
            return u''

        if result.status_code != 200:
            return u""

        unresult = self.__compressor.decompress(result.content)

        try:
            result = json.loads(unresult)["data"]["parsed_html"]
        except (TypeError, ValueError, ):
            result = u''

        return result


def send_request(server, text):
    return ParserClient(server).process(text) or text
