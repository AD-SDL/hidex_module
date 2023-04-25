import os
import sys
import zmq
from datetime import datetime

# TODO: find a better way to access the driver functions
# TODO: put solo driver, ahks, and client in new directory/git repo
sys.path.append('C:\\Users\\svcaibio\\Dev\\hidex_module')
from hidex_driver.ahk import solo_auto_run

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5557")
print("hudson01 listening on port 5557")

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

        if action_handle=="run_protocol": 

            try: 
                # check that protocol file path exists
                if isinstance(action_vars, str) and os.path.exists(action_vars): 
                    is_complete = solo_auto_run.soloRun(action_vars)
                    print(is_complete) # TESTING
                    if is_complete == True:
                        response = "SOLO protocol complete"
                    else: 
                        response = "ERROR: SOLO ahk did not complete"

                else: 
                    print(f"({datetime.now()}) ERROR: SOLO protocol file path cannot be located or has incorrect formatting (action_vars must be a string)")
                
            except Exception as error_msg: 
                print(error_msg)
                response = "ERROR: SOLO client could not run ahk"
           

        # # drawer control actions
        # if action_handle=="open": 
        #     print('opening hidex drawer')
        #     try: 
        #         is_complete = hidex_open_close.hidexOpenClose()
        #         if is_complete == True: 
        #             response = "Hidex opened"
        #         else: 
        #             response = "ERROR: Hidex ahk unable to open drawer"
        #     except Exception as error_msg: 
        #         print("ERROR: Hidex client unable to run open_close.ahk")

        # elif action_handle=="close": 
        #     print('closing hidex drawer')
        #     try: 
        #         is_complete = hidex_open_close.hidexOpenClose()
        #         if is_complete == True: 
        #             response = "Hidex closed"
        #         else: 
        #             response = "ERROR: Hidex ahk unable to close drawer"
        #     except Exception as error_msg: 
        #         print("ERROR: Hidex client unable to run open_close.ahk")

        # # protocol handling actions
        # if action_handle=='run_protocol':
        #     print('running hidex')
            
        #     try: 
        #         # check that action_vars is a string filename and that it exists
        #         if isinstance(action_vars, str) and os.path.exists(action_vars): 
        #             is_complete = hidex_auto_run.hidexRun(action_vars)
        #             print(is_complete)
        #             if is_complete == True:
        #                 response = "Hidex protocol complete"
        #             else: 
        #                 response = "ERROR: Hidex ahk did not complete"

        #     except Exception as error_msg: 
        #         print(error_msg)
        #         response = "ERROR: Hidex client could not run ahk"

        # # TODO: scan data folder for new hidex data file and return path?
        
        socket.send(bytes(response, encoding='utf-8'))
        
socket.close()