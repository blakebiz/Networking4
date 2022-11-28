import socket
import sys


def request_site(host, port, _type, file=''):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(15)
    sock.connect((host, port))
    sock.send(f'{_type} / HTTP/1.1\r\nHost:{host}{("/" + file) * bool(file)} \r\n\r\n'.encode())

    response = b""
    while True:
        try:
            chunk = sock.recv(4096)
            if len(chunk) == 0:     # No more data received, quitting
                break
            response += chunk
        except socket.timeout:
            print('timeout')
            break

    segments = response.split(b'\r\n\r\n')
    header = segments[0]
    body = b''
    if len(segments) > 1:
        for segment in segments[1:]:
            body += segment
    print('header:', header)
    if file:
        print(f'file has been saved as: rec_{file}')
        with open('rec_' + file, 'wb') as f:
            f.write(body)
    else:
        print('body:', body)
    sock.close()


def main():
    args = sys.argv[1:]
    if len(args) not in (3, 4):
        print('arguments not supplied properly in command line, must be manually entered.')
        args = [
            input('Input a host: '),
            input('Input a port: '),
            input('Input request type (GET/POST): '),
            input('Optionally input a file: ')
        ]
    request_site(*args)

main()
request_site('127.0.0.1', 5010, 'GET', 'test.html')

