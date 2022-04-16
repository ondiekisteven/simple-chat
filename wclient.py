import asyncio
import websockets


clients = []


async def hello():
    async with websockets.connect('ws://localhost:8765') as websocket:

        msg = input("write message:  ")
        await websocket.send(msg)
        print("sending {}".format(msg))

        greeting = await websocket.recv()
        print("< {}".format(greeting))

asyncio.get_event_loop().run_until_complete(hello())
