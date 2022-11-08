import json
import socket
import re

class Server:
    def __init__(self):
        self.sockets = []
        self.accepting_connections = True

    def listen(self):
        def accept_connection():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('0.0.0.0', 5011))
            print(dir(sock))
            data = sock.recv(4096)
            sock.settimeout(3)
            self.sockets.append(sock)
            self.initial_connection(sock, data)
        while self.accepting_connections:
            accept_connection()

    def get_response(self, sock, initial_data=b''):
        response = b""
        while True:
            try:
                chunk = sock.recv(4096)
                if len(chunk) == 0:  # No more data received, quitting
                    break
                response += chunk
            except socket.timeout:
                break
        return initial_data + response
    #
    # def seperate_header(self, response):
    #     segments = response.split(b'\r\n\r\n')
    #     header = segments[0]
    #     body = b''
    #     if len(segments) > 1:
    #         for segment in segments[1:]:
    #             body += segment
    #     return header, body

    def initial_connection(self, sock, initial_data):
        response = self.get_response(sock, initial_data)
        pattern = re.compile(r'([^ ]*) */ *HTTP/1.1([^ :]*) ?Host:([^ ]*) +([^ ]*)')
        sub_sep, _type, host, sep = pattern.fullmatch(response.decode()).groups()
        pattern = re.compile(r'(\d+.\d+.\d+.\d+)/(.*)')
        _, file = pattern.fullmatch(host).groups()

        chunks = []
        sub_sep.encode()
        try:
            with open(file, 'rb') as f:
                while chunk := file.read(4096-len(sub_sep)):
                    chunks.append(chunk + sub_sep)
        except FileNotFoundError:
            chunks = [b'FILE NOT FOUND!']

        header = json.dumps({'dummy-data': True})

        sock.send(header.encode() + sep)
        for chunk in chunks:
            sock.send(chunk)
        sock.send(b'')




s = Server()
s.listen()




