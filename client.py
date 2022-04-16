import asyncio
import logging
from socket import socket, AF_INET, SOCK_STREAM

logger = logging.getLogger(__name__)

HOST = ''
BUFF_SIZE = 2048
PORT = 65432
ADDR = (HOST, PORT)


def connect_to_chat():
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall('Steven'.encode())
        while True:
            data = s.recv(1024)
            resp = input(data.decode() + " : ")
            s.sendall(resp.encode())


if __name__ == '__main__':
    connect_to_chat()