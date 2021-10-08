#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Copyright 2021 Tianying Xia 
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
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        words_list = data.split(' ')
        return int(words_list[1])

    def get_headers(self,data):
        header_body_list = data.split('\r\n\r\n')
        return header_body_list[0]

    def get_body(self, data):
        body_or_not_list = data.split('\r\n\r\n')
        if len(body_or_not_list) > 1:
            return body_or_not_list[1]
        return None
    
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
        #code = 500
        #body = ""
        url_parsed = urllib.parse.urlparse(url)  # named tuple 
        loc_split = url_parsed.netloc.split(':')
        host = loc_split[0]
        if len(loc_split) < 2:
            port = 80
        else:
            port = int(loc_split[1])
        path = url_parsed.path
        if path == '':
            path = '/'
        
        self.connect(host, port)
        msg_send = f'GET {path} HTTP/1.1\r\n'
        host_name_str = f'Host: {url_parsed.netloc}\r\n'
        user_agent_str = 'User-Agent: This agent\r\n'
        connection_str = 'Connection: keep-alive\r\n'
        
        msg_send = msg_send + host_name_str + user_agent_str + connection_str + '\r\n'

        self.sendall(msg_send)
        self.socket.shutdown(socket.SHUT_WR)

        msg_recv = self.recvall(self.socket)
        code = self.get_code(msg_recv)
        body = self.get_body(msg_recv)
        self.close()
        print('Status code is', code)
        print('Content: ')
        if body != None:
            print(body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        #code = 500
        #body = ""
        url_parsed = urllib.parse.urlparse(url)  # named tuple 
        loc_split = url_parsed.netloc.split(':')
        host = loc_split[0]
        if len(loc_split) < 2:
            port = 80
        else:
            port = int(loc_split[1])
        path = url_parsed.path
        if path == '':
            path = '/'
        
        self.connect(host, port)
        msg_send = f'POST {path} HTTP/1.1\r\n'
        host_name_str = f'Host: {url_parsed.netloc}\r\n'
        user_agent_str = 'User-Agent: This agent\r\n'
        content_type_str = 'Content-Type: application/x-www-form-urlencoded\r\n'
        connection_str = 'Connection: close\r\n'
        query = []
        if args != None:
            for arg in args:
                value = args[arg].replace(' ', '+')
                query.append(arg.replace(' ', '+') + '=' + value)
        query_str = '&'.join(query)
        content_length_str = 'Content-Length: ' + str( len(query_str) ) + '\r\n'
        
        msg_send = msg_send + host_name_str + user_agent_str + content_type_str + content_length_str + connection_str + '\r\n' + query_str

        self.sendall(msg_send)
        self.socket.shutdown(socket.SHUT_WR)

        msg_recv = self.recvall(self.socket)
        code = self.get_code(msg_recv)
        body = self.get_body(msg_recv)
        self.close()
        print('Status code is', code)
        print('Content: ')
        if body != None:
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
