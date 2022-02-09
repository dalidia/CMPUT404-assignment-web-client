#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Copyright 2022 Lidia Ataupillco-Ramos 
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
# you may use urllib to encode data appropriately
# TODO use this
from urllib.parse import urlparse, urlencode

HTTP_PROTOCOL = 'HTTP/1.1'

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port_path(self, url):
        parse_result = urlparse(url)

        netloc = parse_result.netloc.split(':')
        host = netloc[0]
        port = int(netloc[1]) if len(netloc) > 1 else 80

        path = parse_result.path if parse_result.path else '/'

        return host, port, path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def construct_headers(self, args):
        headers = ''
        for header in args:
            headers += f'{header}: {args[header]}\r\n'
        
        return headers

    def get_code(self, data):
        headers = self.get_headers(data)

        request_line = headers.split('\r\n')[0]

        code = int(request_line.split()[1])
        return code

    def get_headers(self,data):
        parsed_data = data.split('\r\n\r\n')
        
        return parsed_data[0]

    def get_body(self, data):
        parsed_data = data.split('\r\n\r\n')
        
        if len(parsed_data) > 1:
            body = parsed_data[1]
        else:
            body = ''

        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part

        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        host, port, path = self.get_host_port_path(url)

        self.connect(host, port)

        # convert args into form-urlencode
        if args:
            query = "/" + urlencode(args)
        else:
            query = ''

        payload = f'GET {path}{query} {HTTP_PROTOCOL}\r\nHost: {host}:{port}\r\n'

        raw_headers = {
            'Connection': 'close', 
            'Accept-Charset': 'UTF-8',
            'User-Agent': "Lidia's agent", 
            "Content-Type": "text/html;charset=UTF-8"
        }

        # add additional args
        payload += self.construct_headers(raw_headers)

        # add header ending
        payload += '\r\n'

        self.sendall(payload)
        self.socket.shutdown(socket.SHUT_WR)

        data = self.recvall(self.socket)

        # print("DATA", payload)

        self.socket.close()

        code = self.get_code(data)
        body = self.get_body(data)

        print(body)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port, path = self.get_host_port_path(url)

        self.connect(host, port)

        payload = f'POST {path} {HTTP_PROTOCOL}\r\nHost: {host}:{path}\r\n'

        # convert args into form-urlencode
        if args:
            body = urlencode(args)
        else:
            body = ''

        raw_headers = {
            "Content-Type": 'application/x-www-form-urlencoded; charset=UTF-8',
            "Content-Length": f"{len(body.encode('utf-8'))}",
            "User-Agent": "Lidia's agent",
            "Connection": 'close'
        }

        payload += self.construct_headers(raw_headers)

        # add header ending
        payload += '\r\n'

        payload += body

        self.sendall(payload)
        self.socket.shutdown(socket.SHUT_WR)
        data = self.recvall(self.socket)
        self.socket.close()

        code = self.get_code(data)
        body = self.get_body(data)

        print(body)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
