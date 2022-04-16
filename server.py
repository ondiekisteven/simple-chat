import asyncio
import logging
from socket import socket

import websockets

LOG_FORMAT = '%(asctime)s : %(levelname)-7s : %(message)s'

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

HOST = ''
PORT = 65432

USERS = {}


def broadcast(message):
    for user in USERS:
        user.sendall(message.encode())


def handle_user(con: socket):
    logger.info(f"USER {con.getsockname()} has connected..")
    with con:
        while True:
            username = con.recv(1024)
            if not username:
                break
        USERS[username] = con
        logger.info(f'new user {username} has joined the chat.')
        con.sendall(
            f"Welcome {username} to the chat, Enter a command. 'DM <username> <message>' to send direct message, 'PM <message>' to send message to all connected users".encode())

        while True:
            cmd = con.recv(2048)
            if not cmd:
                continue
            msg = cmd.decode()
            if msg.startswith('PM'):
                broadcast(" ".join(msg.split(" ")[1:]))

            elif msg.startswith('DM'):
                username = msg.split(' ')[1]
                msg = " ".join(msg.split(' ')[2:])
                try:
                    soc = USERS[username]
                    soc.sendall(msg.encode())
                except:
                    con.sendall(f"Username '{username}' is not found. ")


if __name__ == '__main__':
    async def hello(websocket):
        name = await websocket.recv()
        print("< {}".format(name))

        greeting = "Hello {}!".format(name)
        await websocket.send(greeting)
        print("> {}".format(greeting))


    start_server = websockets.serve(hello, '', 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
