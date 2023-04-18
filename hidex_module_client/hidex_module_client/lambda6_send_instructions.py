
import argparse
import json
import zmq
import os
import sys


def lamdba6_send_instructions():

    # * connect to port on hudson01
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://hudson01.cels.anl.gov:5556")
    
    
    # Send message to queue
    socket.send_string("BATATA!")
    print("Message sent to port 5556 on hudson01")
    
    # Wait for reply and 
    repl = socket.recv()
    string_repl = str(repl)
    
    print(f"Got {string_repl}")


    socket.close()


def main(args):
    # Parse args

    lamdba6_send_instructions()


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
