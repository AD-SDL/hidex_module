import os
import sys
import socket
from datetime import datetime

# TODO: find a better way to access the driver functions
# TODO: put solo driver, ahks, and client in new directory/git repo
sys.path.append('C:\\Users\\svcaibio\\Dev\\hidex_module')
from hidex_driver.ahk import solo_auto_run

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (socket.gethostname(),5557)
sock.bind(server_address)
sock.listen(1) # listen for one connection at at time
print("hudson01 listening on port 5557")


while True:
    connection, client_address = sock.accept()

    try: 
        message = connection.recv(4096)
        print(f"Received: {message}")

        response = ""

        if message == b"SHUTDOWN":
            connection.sendall(b"Shutting down")
            break

        else:
            msg = eval(message.decode("utf-8"))

            try: # msg is formatted correctly, will hit except if msg is not dictionary

                action_handle = msg['action_handle'] 
                action_vars = msg['action_vars']

                if action_handle=="run_protocol": 

                    try: 
                        # TODO: check that action vars is a dictionary and has entry for protocol path (overkill?)

                        # check that protocol file path exists
                        if isinstance(action_vars['protocol_path'], str) and os.path.exists(action_vars['protocol_path']): 
                            return_dict = solo_auto_run.soloRun(action_vars['protocol_path'])
                            return_dict['action_log'] += (f"{datetime.now()} LISTEN SOLO: SOLO Run Protocol Complete\n")

                        else: 
                            return_dict = {
                                'action_response': -1,
                                'action_log': (f"{datetime.now()} ERROR LISTEN SOLO: SOLO protocol path cannot be located or has incorrect formatting (action_vars must be a string)\n{error_msg}\n")
                            }

                    except Exception as error_msg: 
                        return_dict = {
                            'action_response': -1,
                            'action_log': (f"{datetime.now()} ERROR LISTEN SOLO: SOLO client could not run ahk\n{error_msg}\n")
                        }
                
                else:  # action_handle is not recognized
                    return_dict = {
                        'action_response': -1,
                        'action_log': (f"{datetime.now()} ERROR LISTEN SOLO: message action_handle is not recognized\n{error_msg}\n")
                    }

            except Exception as error_msg: # message is not formatted correctly, could not read action_msg
                return_dict = {
                    'action_response': -1,
                    'action_log': (f"{datetime.now()} ERROR LISTEN SOLO: Message received was not formatted correctly. Could not parse action_handle.\n{error_msg}\n")
                }

    except Exception as error_msg: # message could not be received from connection
        return_dict = {
            'action_response': -1,
            'action_log': (f"{datetime.now()} ERROR LISTEN SOLO: Message could not be received.\n{error_msg}\n")
        }

    finally: 
        response = str(return_dict)
        connection.sendall(bytes(response, encoding='utf-8'))
        connection.close()

sock.close()



            

       