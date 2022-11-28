import json
import socket
import re
import threading
import time


class Server:
    def __init__(self, default_timeout=10, extended_timeout=100, host='0.0.0.0', port=5010):
        self.sock = None
        self.default_timeout = default_timeout
        self.extended_timeout = extended_timeout
        self.host, self.port = host, port


    def accept_connection(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        self.sock, _ = self.sock.accept()
        data = self.get_response(self.sock)
        self.respond(data)

    def get_response(self, sock, extend=False):
        if extend:
            sock.settimeout(self.extended_timeout)
        response = b""
        while True:
            try:
                chunk = sock.recv(4096)
                if len(chunk) == 0:  # No more data received, quitting
                    break
                response += chunk
            except socket.timeout:
                break
            sock.settimeout(self.default_timeout)
        return response

    def respond(self, data):
        pattern = re.compile(r'([^ ]*) */ *HTTP/1.1([^ :]*) ?Host:([^ ]*) +([^ ]*)')
        match = pattern.fullmatch(data.decode())
        if match:
            sub_sep, _type, host, sep = match.groups()
            pattern = re.compile(r'(\d+.\d+.\d+.\d+)/?(.*)')
            _, file = pattern.fullmatch(host).groups()
            try:
                with open(file, 'rb') as f:
                    body_data = f.read()
            except FileNotFoundError:
                body_data = b'FILE NOT FOUND!'

            header = json.dumps({'this-is-a-header': True}).encode()
            chunks = seperate_chunks(header + sep.encode() + body_data)
            print(chunks)
            for chunk in chunks:
                self.sock.send(chunk)
            self.sock.send(b'')
            self.sock.close()
            self.accept_connection()
        else:
            self.sock.send(b'Invalid request, closing connection. To retry, reconnect.')
            self.sock.send(b'')
            self.sock.close()
            self.accept_connection()


def seperate_chunks(data , length=4096):
    counter, chunks = 0, []
    while counter < len(data):
        chunks.append(data[counter:length])
        counter += length
    return chunks

s = Server()
s.accept_connection()




