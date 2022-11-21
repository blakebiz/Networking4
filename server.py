import json
import socket
import re
import threading


class Server:
    def __init__(self, default_timeout=10, extended_timeout=100, host='0.0.0.0', port=5010):
        self.sockets = []
        self.accepting_connections = True
        self.default_timeout = default_timeout
        self.extended_timeout = extended_timeout

        self.host, self.port = host, port

    def listen(self):
        def accept_connection():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((self.host, self.port))
            sock.listen(1)
            sock, _ = sock.accept()
            data = self.get_response(sock)
            sock.settimeout(self.default_timeout)
            self.sockets.append(sock)
            threading.Thread(target=self.make_connection, args=(sock, data)).start()

        while self.accepting_connections:
            accept_connection()

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
    #
    # def seperate_header(self, response):
    #     segments = response.split(b'\r\n\r\n')
    #     header = segments[0]
    #     body = b''
    #     if len(segments) > 1:
    #         for segment in segments[1:]:
    #             body += segment
    #     return header, body

    def make_connection(self, sock, response):
        pattern = re.compile(r'([^ ]*) */ *HTTP/1.1([^ :]*) ?Host:([^ ]*) +([^ ]*)')
        match = pattern.fullmatch(response.decode())
        if match:
            sub_sep, _type, host, sep = match.groups()
            pattern = re.compile(r'(\d+.\d+.\d+.\d+)/(.*)')
            _, file = pattern.fullmatch(host).groups()
            chunks = []
            sub_sep.encode()
            try:
                with open(file, 'rb') as f:
                    while chunk := f.read(4096-len(sub_sep)):
                        chunks.append(chunk + sub_sep)
            except FileNotFoundError:
                chunks = [b'FILE NOT FOUND!']

            header = json.dumps({'dummy-data': True})
            sock.send(header.encode() + sep)
            for chunk in chunks:
                sock.send(chunk)
            sock.send(b'')
            self.wait_for_command(sock)
        else:
            sock.send(b'Invalid request, closing connection. To retry, reconnect.')
            sock.send(b'')

    def wait_for_command(self, sock):
        response = self.get_response(sock, extend=True)
        if response.startswith(b'CLOSE_CONNECTION'):
            sock.send(b'CONNECTION_CLOSED')
            sock.send(b'')
            sock.close()
        else:
            self.make_connection(sock, response)

s = Server()
s.listen()




