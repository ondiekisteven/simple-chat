#!/usr/bin/python3
import json
import logging
import socket
import sys

from _thread import *

LOG_FORMAT = '%(asctime)s : %(levelname)-7s : %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

authenticated_users = {}


def get_data():
    """
    function for getting data from json file, that is going to be our database
    """
    filename = 'users_data.json'
    f = open(filename, 'r')
    data = json.load(f)
    f.close()
    return data


def save_progress(data):
    """
    for updating database
    """
    filename = 'users_data.json'
    f = open(filename, "w")
    json.dump(data, f, indent=4)
    f.close()


def update_user(user_id, data):
    """
    updating user's data
    """
    d = get_data()
    for key in data.keys():
        d[user_id][key] = data[key]

    save_progress(d)


def prompt(conn):
    conn.sendall("[OK] Enter command ")


def client_thread(conn):
    """
    The thread handling the user lifecycle
    """
    username = None

    while True:
        """
        This first while-loop is for taking the user's username, 
        Once the username has been retrieved, this loop exits.
        """
        _username = conn.recv(2048)

        if _username:  # if there is data in the socket...
            username = _username.decode().strip()
            usr = get_data()

            if username in usr:  # checking if the user is stored in our database and prompting for their password

                conn.sendall('Enter password: '.encode())
                d = {'app': 'PM', 'step': 2, 'authenticated': False}
                update_user(username, d)
            else:  # user is not registered, so we register them then ask for their password
                usr[username] = {
                    'username': username,
                    'password': None,
                    'step': 1,
                    'authenticated': False,
                    'app': None
                }
                authenticated_users[_username] = conn
                save_progress(data=usr)

                conn.sendall('Enter password: '.encode())
            break

    while True:
        try:
            message = conn.recv(2048)

            if message:
                user = get_data()[username]  # load user data from database

                if not user['authenticated']:
                    password = message.decode().strip()
                    d = {
                        'step': 1,
                        'app': None
                    }
                    if user['password'] is None:  # is a new user, we save their password and authenticated state
                        d['password'] = password
                        d['authenticated'] = True
                        update_user(username, d)
                        authenticated_users[username] = conn
                        conn.sendall(
                            f"Welcome to this chatroom! Enter command : ".encode())
                    else:  # user is not new, checking their password in database
                        if user['password'] == password:
                            d['authenticated'] = True
                            update_user(username, d)
                            authenticated_users[username] = conn  # adding them to authenticated (online) users
                            conn.sendall(
                                f"Welcome to this chatroom! There are {len(authenticated_users)} "
                                f"clients.  Enter command : ".encode())
                        else:
                            conn.sendall(
                                f"Password Incorrect. Try again".encode())

                else:
                    msg = message.decode().strip()
                    logger.info(f'user data: {user}')
                    logger.info(f'connected: {authenticated_users.keys()}')

                    if msg == 'EX':
                        conn.sendall('EXIT'.encode())  # we send EXIT back to them so they exit on their side too
                        logout_user(username)
                        exit_thread()

                    elif user['step'] == 1 and msg == 'PM' or msg == 'PM':
                        d = {'app': 'PM', 'step': 2}
                        update_user(username, d)
                        conn.sendall('[*] ENTER MESSAGE TO SEND: '.encode())

                    elif user['step'] == 1 and msg == 'DM' or msg == 'DM':
                        d = {'app': 'DM', 'step': 2}
                        update_user(username, d)
                        online_users = "Here are online users\n\n" + "\n".join([i for i in authenticated_users.keys()])
                        conn.sendall(online_users.encode())
                        conn.sendall('\nEnter username of user to send: '.encode())

                    elif user['step'] == 2 and user['app'] == 'PM':
                        for con in authenticated_users.values():
                            if con != conn:
                                d = {'app': None, 'step': 1}
                                con.sendall(msg.encode())
                                update_user(username, d)
                        prompt(conn)

                    elif user['step'] == 2 and user['app'] == 'DM':
                        if msg in authenticated_users:
                            if authenticated_users[msg] == conn:
                                conn.sendall(f'YOU CANNOT SEND DM TO YOURSELF'.encode())
                                d = {'app': None, 'step': 1}
                                update_user(username, d)
                            else:

                                # we save this username so as to use it later after asking for the message to be sent
                                d = {'dm_to_username': msg, 'step': 3}
                                update_user(username, d)
                                conn.sendall(f'[*] ENTER MESSAGE TO SEND TO {msg} : '.encode())
                        else:
                            conn.sendall(f'{msg} not found in list of online users. Start afresh'.encode())
                            d = {'app': None, 'step': 1}
                            update_user(username, d)

                    elif user['step'] == 3 and user['app'] == 'DM':
                        con = authenticated_users[user['dm_to_username']]
                        logger.info(f"sending DM message to {con}...")
                        d = {'app': None, 'step': 1}
                        con.sendall(msg.encode())
                        update_user(username, d)
                        prompt(conn)

                # broadcast(message_to_send, conn)
        except KeyboardInterrupt:
            conn.sendall('EXIT'.encode())
            logout_user(username)

        except ConnectionResetError:
            logout_user(username)
            exit_thread()

        except Exception as e:
            logger.exception(str(e))
            continue


def logout_user(user):
    """
    logs a user out of the chat. If the user is authenticated, we remove them from authenticated (online) users
    We also change their authenticated status to False (so they enter password next time)
    """
    if user in authenticated_users:
        del authenticated_users[user]
    d = {
        'authenticated': False,
        'app': None
    }
    update_user(user, d)
    logger.info("LOGGING OUT")


def handle_connections():

    """
    Handles new connections. For each new connection, it creates a thread to handle the user.
    """
    while True:
        connection, addr = server.accept()
        logger.info(f"{addr} connected")
        start_new_thread(client_thread, (connection,))


if __name__ == '__main__':
    try:

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if len(sys.argv) != 2:
            logger.info("Correct usage: script, IP address, port number")
            exit()
        Port = int(sys.argv[1])  # get port from second argument

        server.bind(('', Port))
        server.listen(100)  # listen for 100 incoming connections
        logger.info(f'running server  on 0.0.0.0:{Port}')

        # start accepting connections
        handle_connections()
        server.close()
    except Exception as e:
        logger.exception(e)
        for __user in authenticated_users.keys():
            logger.info(f"sending exit message to {__user}...")
            __d = {'app': None, 'step': 1, 'authenticated': False}
            authenticated_users[__user].sendall('EXIT'.encode())
            update_user(__user, __d)

