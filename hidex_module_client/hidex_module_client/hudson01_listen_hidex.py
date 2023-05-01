import os
import sys
import zmq

# TODO: find a better way to access the driver functions
sys.path.append('C:\\Users\\svcaibio\\Dev\\hidex_module')
from hidex_driver.ahk import hidex_auto_run, hidex_open_close

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5556")
print("hudson01 listening on port 5556")

while True:
    message = socket.recv()
    response = ""
    if message == b"SHUTDOWN":
        socket.send(b"Shutting down")
        break
    else:
        msg = eval(message.decode("utf-8"))

        #check if msg is dictionary
        action_handle = msg['action_handle'] 
        action_vars = msg['action_vars']

        # drawer control actions
        if action_handle=="open": 
            print('opening hidex drawer')
            try: 
                is_complete = hidex_open_close.hidexOpenClose()
                if is_complete == True: 
                    response = "Hidex opened"
                else: 
                    response = "ERROR: Hidex ahk unable to open drawer"
            except Exception as error_msg: 
                print("ERROR: Hidex client unable to run open_close.ahk")

        elif action_handle=="close": 
            print('closing hidex drawer')
            try: 
                is_complete = hidex_open_close.hidexOpenClose()
                if is_complete == True: 
                    response = "Hidex closed"
                else: 
                    response = "ERROR: Hidex ahk unable to close drawer"
            except Exception as error_msg: 
                print("ERROR: Hidex client unable to run open_close.ahk")

        # protocol handling actions
        if action_handle=='run_protocol':
            print('running hidex')
            
            try: 
                # check that action_vars is a string filename and that it exists
                if isinstance(action_vars['protocol_path'], str) and os.path.exists(action_vars['protocol_path']): 
                    # TESTING 
                    print(action_vars['protocol_path'])
                    return_dict = hidex_auto_run.hidexRun(action_vars['protocol_path'])
                    response = str(return_dict)  # this is the right form

            except Exception as error_msg: 
                print(error_msg)
                response = "ERROR: Hidex client could not run ahk"
        
        socket.send(bytes(response, encoding='utf-8')) 

        
socket.close()