import socket
import sys


def request_site(host, port, _type, file=''):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((host, port))
    sock.send(f'{_type} / HTTP/1.1\r\nHost:{host}{("/" + file) * bool(file)}\r\n\r\n'.encode())

    response = b""
    while True:
        try:
            chunk = sock.recv(4096)
            if len(chunk) == 0:     # No more data received, quitting
                break
            response += chunk
        except TimeoutError:
            break

    segments = response.split(b'\r\n\r\n')
    header = segments[0]
    body = b''
    if len(segments) > 1:
        for segment in segments[1:]:
            body += segment

    with open('test.html', 'wb') as f:
        f.write(body)

    sock.close()

def main():
    args = sys.argv
    if len(args) not in (3, 4):
        raise ValueError('Invalid amount of arguments supplied: Must supply (host, port_number, type, [filename])')
    request_site(*args)


