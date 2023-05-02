import os
import sys
import zmq
from datetime import datetime

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

        try:  # msg is formatted correctly
            
            #check if msg is dictionary
            action_handle = msg['action_handle'] 
            action_vars = msg['action_vars']

            # drawer control actions
            if action_handle=="open": 

                try: 
                    return_dict = hidex_open_close.hidexOpenClose()
                    return_dict['action_log'] += (f"{datetime.now()} LISTEN HIDEX: Hidex Opened\n")
                    response = str(return_dict)

                except Exception as error_msg: 
                    return_dict = {
                        'action_response': -1,
                        'action_log': (f"{datetime.now()} ERROR LISTEN HIDEX: Hidex client unable to run open_close.ahk\n{error_msg}")
                    }
                    response = str(return_dict)

            elif action_handle=="close":  # same as open for now

                try: 
                    return_dict = hidex_open_close.hidexOpenClose()
                    return_dict['action_log'] += (f"{datetime.now()} LISTEN HIDEX: Hidex Closed\n")
                    response = str(return_dict)

                except Exception as error_msg: 
                    return_dict = {
                        'action_response': -1,
                        'action_log': (f"{datetime.now()} ERROR LISTEN HIDEX: Hidex client unable to run open_close.ahk\n{error_msg}")
                    }
                    response = str(return_dict)

            # protocol handling actions
            if action_handle=='run_protocol':
                
                try: 
                    # check that action_vars is a string filename and that it exists
                    if isinstance(action_vars['protocol_path'], str) and os.path.exists(action_vars['protocol_path']): 
                        return_dict = hidex_auto_run.hidexRun(action_vars['protocol_path'])
                        return_dict['action_log'] += (f"{datetime.now()} LISTEN HIDEX: Hidex Run Protocol Complete\n")
                        response = str(return_dict) 

                except Exception as error_msg: 
                    return_dict = {
                        'action_response': -1,
                        'action_log': (f"{datetime.now()} ERROR LISTEN HIDEX: Hidex client could not run ahk\n{error_msg}\n")
                    }
                    response = str(return_dict)
        
        except Exception as error_msg:  # msg is not formatted correctly
            return_dict = {
                'action_response': -1,
                'action_log': (f"{datetime.now()} ERROR LISTEN HIDEX: Message received was not formatted correctly\n{error_msg}\n")
            }
            response = str(return_dict)

        socket.send(bytes(response, encoding='utf-8')) 
    
socket.close()