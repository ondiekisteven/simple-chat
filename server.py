import asyncio
import logging
import pathlib
import ssl

import websockets

LOG_FORMAT = '%(asctime)s : %(levelname)-7s : %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
localhost_pem = pathlib.Path(__file__).with_name('localhost.pem')
ssl_context.load_cert_chain(localhost_pem)

AUTH = {}


def handle_chat_messages():
    return 'message sent'


async def handle_messages(websocket):
    msg = await websocket.recv()
    logger.info(f"new message : {msg}")
    if msg in ['PM', 'DM']:
        resp = handle_chat_messages()
    else:
        logger.info(AUTH)
        if msg in AUTH:
            resp = "COMMAND_ERROR"
        else:
            logger.info(f"new client connection : {websocket!r}")
            AUTH[msg] = websocket
            resp = "CONNECTED"

    await websocket.send(resp)


async def main():
    async with websockets.serve(handle_messages, 'localhost', 8765, ssl=ssl_context):
        await asyncio.Future()


if __name__ == '__main__': 
    asyncio.run(main())
