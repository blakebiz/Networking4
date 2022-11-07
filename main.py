import socket
import time
import threading

class Result:
    def __init__(self):
        self.response = None

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(('www.google.com', 80))
sock.send(b'GET / HTTP/1.1\r\nHost:www.google.com\r\n\r\n')
response = b""
while True:
    print('waiting')
    no_response = False
    start = time.time()
    result = Result()
    def get_response(res):
        res.response = sock.recv(4096)

    threading.Thread(target=get_response, args=(result,)).start()
    while result.response is None:
        print('looping')
        time.sleep(.2)
        if time.time() - start > 5:
            no_response = True
            break
    else:
        if len(result.response) == 0:     # No more data received, quitting
            break
        else:
            print(len(result.response), result.response)
        response += result.response;
    print(no_response)
    if no_response:
        break
print('done')
# print(response)
with open('test.html', 'w') as f:
    f.write(response.decode())
# print(response.decode())
sock.close()