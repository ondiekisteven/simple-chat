import socket
import select
import sys


def join_chat():
    try:
        while True:

            sockets_list = [sys.stdin, server]

            read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])

            for socks in read_sockets:
                if socks == server:
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
