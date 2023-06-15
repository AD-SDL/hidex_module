import zmq
import sys


def send_instructions(tcp_address='hudson01.cels.anl.gov',tcp_port='11139'):

    # * connect to tcp_port on hudson01
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://"+tcp_address+":"+tcp_port)
    

    msg = 'GETSTATUS\r\n'
    # Send message to queue
    socket.send_string(str(msg))
    print("Message sent to tcp_port " + tcp_port +" on " + tcp_address)
    
    # Wait for reply and 
    repl = socket.recv()
    string_repl = str(repl)
    
    print(f"Got {string_repl}")


    socket.close()


def main(args):
    send_instructions()


if __name__ == "__main__":
    main(sys.argv)
