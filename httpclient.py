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
import re
# you may use urllib to encode data appropriately
# TODO use this
import urllib.parse

# TODO: do we need to handle when there's no port
# TODO: protocol 1.1?
HTTP_PROTOCOL = 'HTTP/1.1'

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body
    
    def create_headers(self):
        pass

class HTTPClient(object):
    def get_host_port_path(self, url):
        url_regex = r'https?:\/\/([0-9a-zA-Z\.]+):(\d+)(\/[\w\/]+)?'
        host, port, path = re.search(url_regex, url).groups()
        return host, port, path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def construct_headers(self, args):
        headers = ''
        for key, val in args:
            headers += f'{key}:{val}\r\n'
        
        return headers

    def get_code(self, data):
        return None

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return None
    
    def get_info(self, data):
        parsed_data = data.split('\r\n\r\n')

        code = parsed_data[0].split('\r\n')[0].split()[1]
        body = parsed_data[1]

        return int(code), body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        print("SOCKET", sock)

        # buffer = bytearray()
        buffer = ''.encode('utf-8')
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer += part
            else:
                done = not part

        # check for incoming data greater than the buffer size
        # while True:
        #     data = sock.recv(4096)
        #     if not data:
        #         break
        #     buffer += data
        return buffer.decode('utf-8', 'ignore')

    def GET(self, url, args=None):
        # TODO add connect
        host, port, raw_path = self.get_host_port_path(url)
        self.connect(host, int(port))
        path = raw_path if raw_path is not None else '/'
        payload = f'GET {path} {HTTP_PROTOCOL}\r\nHost: {host}\r\n'

        # add additional args
        # TODO do I need to add extra headers like connection, date, accept, content-type, content-length
        if args:
            payload += self.construct_headers(args)

        # add ending
        payload += '\r\n'

        self.sendall(payload)
        self.socket.shutdown(socket.SHUT_WR)

        data = self.recvall(self.socket)

        code, body = self.get_info(data)
        # code = 500
        # body = ""
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
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
