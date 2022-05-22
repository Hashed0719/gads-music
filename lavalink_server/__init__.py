from doctest import REPORT_ONLY_FIRST_FAILURE
import os
import subprocess
import threading
import socket


DEFAULT_SERVER_PATH = "lavalink_server/"
HOST = "localhost"
PORT = 2333
PASSWORD = "connect"


def invoke_at(path):
    def wrapper(func):
        def wrap(*args, **kwargs):
            cwd = os.getcwd()

            try:
                os.chdir(path=path)
                func(*args, **kwargs)
            finally:
                os.chdir(cwd)
            
        return wrap
    return wrapper



def initialize_server(path=None):
    if not path:
        path = DEFAULT_SERVER_PATH

    try:
        cwd = os.getcwd()
        os.chdir(path)
        subprocess.Popen("java -jar Lavalink.jar", shell=True)
    finally:
        os.chdir(cwd)

def port_in_use(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        s.shutdown(2)
        return True
    except:
        return False

def wait_until_running():
    running = False
    while not running:
        running = port_in_use(host=HOST, port=PORT)
        print("checking port")


start = threading.Thread(target=initialize_server).start

