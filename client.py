import asyncio
import logging
import pathlib
import ssl

import websockets

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
localhost_pem = pathlib.Path(__file__).with_name('localhost.pem')
ssl_context.load_verify_locations(localhost_pem)

logger = logging.getLogger(__name__)


async def connect_to_chat():
    url = 'wss://localhost:8765'
    async with websockets.connect(url, ssl=ssl_context) as socket:
        name = input("Enter name : ")
        await socket.send(name)
        while True:
            resp = await socket.recv()
            if resp == 'COMMAND_ERROR':
                command = input("Please enter a valid command. Commands can be either 'PM' for public messages or 'DM' for private messages")
            else:
                logger.info(resp)
                command = input('Enter next command : ')

            await socket.send(command)
            await asyncio.sleep(1)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect_to_chat())
