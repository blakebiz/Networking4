import multiprocessing
import os


def setup():
    os.system('python server.py')

def test_client_get():



def main():
    # start our server on a separate process so the client code isn't blocked
    server_process = multiprocessing.Process(target=setup)
    server_process.start()

    server_process.close()


if __name__ == '__main__':
    main()

