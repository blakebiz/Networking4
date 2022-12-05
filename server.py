import json
import os
import socket
import re
from typing import Union, List


class Server:
    def __init__(self,
                 host: str = '0.0.0.0',
                 port: int = 5010,
                 default_timeout: int = 10,
                 extended_timeout: int = 100):
        self.sock = None
        self.default_timeout = default_timeout
        self.extended_timeout = extended_timeout
        self.host, self.port = host, port

    def accept_connection(self) -> None:
        """
        waits for a connection to be made from a client, then responds
        """
        # create new socket with reusable address option
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind socket to given host/port
        self.sock.bind((self.host, self.port))
        # allow the socket to accept 1 connection at most
        self.sock.listen(1)
        # wait for the client to connect
        self.sock, _ = self.sock.accept()
        # get request sent by the client
        data = self.get_response(self.sock)
        # respond to the given request
        self.respond(data)

    def get_response(self, sock: socket.socket, extend: bool = False) -> bytes:
        """
        :param sock: active socket to listen for a response from
        :param extend: whether to extend the timeout or not
        :return: the response from the given socket

        listens for a response from a given socket and returns the response
        """
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

    def respond(self, data: bytes) -> None:
        """
        :param data: The data to respond to

        reads the given data and sends the appropriate response to the client
        """
        # use regex to both validate the data, and extract the information I care about
        pattern = re.compile(r'^([^ ]*) / HTTP/1.1([^ :]*) ?Host:([^ ]*) +([^ ]*) ?(.*)$')
        match = pattern.fullmatch(data.decode())
        # make sure the data matches the expected format, if not reject the request
        if match:
            # extract necessary data if request matches pattern
            _type, sub_sep, host, sep, body = match.groups()
            # from the given host/filename, extract the given file and throw away the host
            pattern = re.compile(r'\d+\.\d+\.\d+\.\d+/?(.*)')
            # get the groups (tuple) and index the first (and only) group
            file = pattern.fullmatch(host).groups()[0]
            # if the request specifies a PUT type, call receive_file and exit function
            if _type == 'PUT':
                return self.receive_file(file, body)
            # if the request specifies a GET type, send the requested file to the client
            try:
                # read data from given file if it exists
                with open(file, 'rb') as f:
                    body_data = f.read()
                # if data is successfully read, set the status of the header to 200
                header = json.dumps({'status-code': 200}).encode()
            except FileNotFoundError:
                # if file is not found, return a 404 error to notify the client
                body_data = b'FILE NOT FOUND!'
                header = json.dumps({'status-code': 404}).encode()

            # separate the data into chunks (not necessary, see separate_chunks function)
            chunks = separate_chunks(header + sep.encode() + body_data)
            # send each chunk to the client
            for chunk in chunks:
                self.sock.send(chunk)
            # data sent, close connection
            self.sock.close()
            # client connection closed, begin waiting for a new connection
            self.accept_connection()
        else:
            # invalid request given, notify client
            self.sock.send(b'Invalid request, closing connection. To retry, reconnect.')
            # close connection to client
            self.sock.close()
            # begin waiting for a new connection
            self.accept_connection()

    def receive_file(self, file: str, body: str) -> None:
        """
        :param file: the filename to store the data as
        :param body: the data to store in the file

        stores the given body data in the given filename
        """
        # make srec (server received) directory if it doesn't exist
        if not os.path.isdir('srec'):
            os.mkdir('srec')
        # save data in srec directory with given filename
        if file:
            print(f'file has been saved as: srec/{file}')
            with open('srec/' + file, 'w') as f:
                f.write(body)
        else:
            print('body:', body)
        # close the connection
        self.sock.close()


def separate_chunks(data: Union[bytes, str],
                    length: int = 4096
                    ) -> List[Union[bytes, str]]:
    """
    :param data: the data to separate
    :param length: the length each chunk should be
    :return: the data given separated into chunks of the given length

    I realized after I wrote this I can just send all the data I don't need to
    separate it manually. But I already wrote this so it's staying.
    """
    counter, chunks = 0, []
    while counter < len(data):
        chunks.append(data[counter:length])
        counter += length
    return chunks


def main():
    """
    create a server object and accept the first connection
    """
    s = Server()
    s.accept_connection()


if __name__ == '__main__':
    main()

