import socket
import time


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
sock.connect(('www.google.com', 80))
sock.send(b'GET / HTTP/1.1\r\nHost:www.google.com\r\n\r\n')

response = b""
while True:
    try:
        chunk = sock.recv(4096)
        if len(chunk) == 0:     # No more data received, quitting
            break
        response += chunk
    except TimeoutError:
        break

# print(response)
with open('test.html', 'wb') as f:
    f.write(response)
# print(response.decode())
sock.close()