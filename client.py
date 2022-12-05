import os
import socket
import sys


def request_site(host: str, port: int, _type: str, file: str = '') -> None:
    """
    :param host: server ip or domain to request to
    :param port: server port
    :param _type: GET or PUT request
    :param file: name of file to request, if requesting one

    Performs a GET or PUT request to a given host and port
    """
    # make sure proper type was given
    _type = _type.upper()
    assert _type in ('GET', 'PUT')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect((host, port))
    sock.send(f'{_type} / HTTP/1.1\r\nHost:{host}{("/" + file) * bool(file)} \r\n\r\n '.encode())
    if _type == 'GET':
        receive_file(sock, file)
    else:
        send_file(sock, file)


def receive_file(sock: socket.socket, file: str) -> None:
    """
    :param sock: active socket to read from
    :param file: name to save the file as

    Reads the data from the socket and stores it in the given filename
    """
    response = b""
    # read all the data being sent and store it in response
    while True:
        try:
            chunk = sock.recv(4096)
            if len(chunk) == 0:     # No more data received, quitting
                break
            response += chunk
        except socket.timeout:
            print('timeout')
            break
    # separate body and header
    segments = response.split(b'\r\n\r\n')
    header = segments[0]
    body = b''
    # if seperator found in body data, append to body
    if len(segments) > 1:
        for segment in segments[1:]:
            body += segment
    print('header:', header)
    # make crec (client received) directory if it doesn't exist
    if not os.path.isdir('crec'):
        os.mkdir('crec')
    # save data in crec directory with given filename
    if file:
        print(f'file has been saved as: crec/{file}')
        with open('crec/' + file, 'wb') as f:
            f.write(body)
    else:
        print('body:', body)
    # close the connection
    sock.close()


def send_file(sock: socket.socket, file: str) -> None:
    """
    :param sock: active socket to send to
    :param file: name of file to send

    sends the data from the given file to the given socket
    """
    # try to find the file given, if not error, if found send data
    try:
        with open(file, 'rb') as f:
            body_data = f.read()
    except FileNotFoundError:
        raise Exception(f'given file: {file} does not exist')
    sock.send(body_data)
    sock.send(b'')
    sock.close()


def main():
    """
    takes input from command line, or requests input if not given, and calls the appropriate function
    """
    args = sys.argv[1:]
    # if unexpected amount of arguments given, prompt for them
    if len(args) not in (3, 4):
        print('arguments not supplied properly in command line, must be manually entered.')
        args = [
            input('Input a host: '),
            int(input('Input a port: ')),
            input('Input request type (GET/POST): '),
            input('Optionally input a file: ')
        ]
    request_site(*args)

main()
# request_site('127.0.0.1', 5010, 'PUT', 'test.html')

