
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
    if message == b"SHUTDOWN":
        socket.send(b"Shutting down")
        break
    else:
        msg = eval(message.decode("utf-8"))
        #check if msg is dictionary
        action_handle = msg['action_handle'] 
        action_vars = msg['action_vars']
        if action_handle=='run_protocol':
            print('running hidex')
            #run ahk 
            #wait
            #get some meaninful response
        response = "Hudson01 received: " + action_handle  
        socket.send(bytes(response, encoding='utf-8'))
        
socket.close()