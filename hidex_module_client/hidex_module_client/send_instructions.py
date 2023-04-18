
import argparse
import json
import zmq
import os
import sys


def send_instructions(tcp_address='hudson01.cels.anl.gov',tcp_port='5556'):

    # * connect to tcp_port on hudson01
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://"+tcp_address+":"+tcp_port)
    
    msg = {
        "action_handle": "run_protocol",
        "action_vars": "/home/rpl/workspace/rpl_workcell/pcr_workcell/protocol_files/solo_beta_test_first.yaml",
    }
    # msg = 'SHUTDOWN'
    # Send message to queue
    socket.send_string(str(msg))
    print("Message sent to tcp_port " + tcp_port+" on "+tcp_address)
    
    # Wait for reply and 
    repl = socket.recv()
    string_repl = str(repl)
    
    print(f"Got {string_repl}")


    socket.close()


def main(args):
    # Parse args

    send_instructions()


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
