
import os
import sys

# from zeromq.test.hudson01_handle_message import hudson01_handle_message
import zmq
import time
import json
import _thread
import threading
from subprocess import Popen

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5556")
print("hudson01 listening on port 5556")

while True:
    message = socket.recv()
    decoded = message.decode("utf-8")

    if message == b"SHUTDOWN":
        socket.send(b"Shutting down")
        break

    else:
        # pass message to hudson01_handle_message
        # child_message_handler = child_pid = Popen(["python", "C:\\Users\\svcaibio\\Dev\\liquidhandling\\zeromq\\test\\hudson01_handle.py", decoded],
        #     start_new_session=True
        #     ).pid

        # address, info, message_body = decoded.split("***")
        # info += "," + address
        print(decoded) 
        response = bytes("Hudson01 received instruction***", encoding='utf-8')
        socket.send(response)
        #socket.send(b"Hudson01 received instruction")
        
