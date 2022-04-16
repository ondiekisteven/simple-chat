#!/usr/bin/python3

"""
For the client, we use the select operation to get inputs from the user.

Since at any time a socket may receive messages, or a user may want to send a message, we pass the server and stdin as
possible inputs to be selected.
When a message is available in any of them, it is printed.

With this, the user can input their message anytime, and messages from the server can be printed without being blocked
in a single thread.


Commands:
    PM - Sending a public message (broadcast to all online users)
    DM - Sending a private message to a specific user
    EX - Exiting from teh chat
"""
import socket
import select
import sys


def join_chat():
    try:
        while True:

            sockets_list = [sys.stdin, server]  # the list of possible input sources

            read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])

            for socks in read_sockets:
                if socks == server:  # messages from the server
                    message = socks.recv(2048)
                    if message:
                        if message.decode().strip() == 'EXIT':
                            print("exiting...")
                            exit(0)
                        print(message.decode())
                else:
                    message = sys.stdin.readline()
                    server.send(message.encode())
    except KeyboardInterrupt:
        server.send('EX'.encode())
    server.close()


if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if len(sys.argv) != 4:
        print("Correct usage: script, IP address, port number")
        exit()
    IP_address = str(sys.argv[1])
    Port = int(sys.argv[2])
    server.connect((IP_address, Port))

    server.send(sys.argv[3].encode())
    join_chat()
