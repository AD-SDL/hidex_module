import os
import sys
import wmi
import psutil
import time
from datetime import datetime

from ahk import AHK
from ahk.window import Window


def soloRun(solo_hso_path):

    action_log = ""
    action_msg = []

    ahk = AHK()

    try: 
    
        # make sure that the SOLO app isn't already running
        if not solo_already_running():

            os.system('start C:\\"Program Files (x86)"\\"Hudson Robotics"\SoloSoft\SOLOSoft.exe') 

            # wait for SoloSoft to open fully
            time.sleep(7)    

            # press enter twice to bypass login screen 
            ahk.key_press("Enter")
            ahk.key_press("Enter")
            
            try: 
                # capture the active window
                soloSoft_window = ahk.win_get(title="C:\Program Files (x86)\Hudson Robotics\SoloSoft\SOLOSoft")
                action_log += (f"({datetime.now()}) window = {str(soloSoft_window)}")

                # make the window full screen
                soloSoft_window.maximize()

                # press 'Open File' button
                ahk.click(34,57)   

                # insert path of hso protocol 
                time.sleep(3)
                ahk.type(solo_hso_path)

                time.sleep(.5)
                ahk.key_press("Enter")

                # press run button then "Enter" to bypass the "Are you sure?" screen
                time.sleep(.5)
                ahk.mouse_move(195,59)
                ahk.click()
                time.sleep(.5)
                ahk.key_press("Enter")
                
                # ---- SOLO program is now running! --------------

                # monitor for "Running Method..." or "Run Stopped" windows
                time.sleep(.5)
                while True: 
                    try: 
                        # monitor run progress, locate status windows
                        run_completed_window = ahk.find_window(title=b'SOLOSoft',text=b'OK\r\nRun Completed.\r\n')
                        run_stopped_window = ahk.find_window(title=b'SOLOSoft',text=b'OK\r\nRun Stopped.\r\n')
                        still_running_window = ahk.find_window(title=b"Running Method...")

                        # TESTING - can be removed later
                        action_log += (f"({datetime.now()}) Run completed: {str(True if run_completed_window else False)}\n")
                        action_log += (f"({datetime.now()}) Run stopped: {str(True if run_stopped_window else False)}\n")
                        action_log += (f"({datetime.now()}) Still running: {str(True if still_running_window else False)}\n")
                        action_log += (f"({datetime.now()}) ----------------------------\n")

                        # check for one of the following states
                        if still_running_window and not (run_stopped_window or run_completed_window): 
                            # solo protocol is still running
                            action_log += (f"({datetime.now()}) SOLO AHK STATUS: hso running\n") 

                        elif not still_running_window and run_stopped_window: 
                            # protocol does not register as running or completed = error 
                            action_response = -1
                            action_log += (f"({datetime.now()}) SOLO AHK STATUS: hso protocol stopped, see SoloSoft app for error details\n")
                            break

                        elif not still_running_window and run_completed_window: 
                            # solo protocol is completed
                            action_log += (f"({datetime.now()}) SOLO AHK STATUS: hso run completed\n")
                            time.sleep(1)

                            # close down the SOLOSoft app after the run
                            killed_SOLOSoft = False
                            for proc in psutil.process_iter():

                                if proc.name() == "SOLOSoft.exe":
                                    proc.kill()
                                    action_log += (f"({datetime.now()}) SoftLinx shut down complete\n")

                                    # format response message variables
                                    action_response = 0
                                    action_log += (f"({datetime.now()}) Action Complete: SOLO Run Program\n")

                                    killed_SOLOSoft = True
                                    break  
                                
                            if killed_SOLOSoft == False: 
                                # could not locate and kill the SOLOSoft.exe
                                action_response = -1
                                action_log += (f"({datetime.now()}) ERROR SOLO AHK: SOLO run complete but could not locate and close SOLOSoft.exe.\n{error_msg}\n")
                            
                        else:  
                            # some other intermediate run status hit TODO: what would this be?/how to handle
                            # TODO: how to handle this state?/what would it be?
                            action_log += (f"({datetime.now()}) SOLO AHK STATUS: TODO: handle this intermediate state\n")
                   
                    except Exception as error_msg: 
                        action_response = -1
                        action_log += (f"({datetime.now()} SOLO AHK: Could not locate run status windows.\n{error_msg}\n")
                    
                    time.sleep(2)

            except Exception as error_msg:
                action_response = -1
                action_log += (f"({datetime.now()}) ERROR SOLO AHK: Unable to complete SOLO ahk run protocol.\n{error_msg}\n")   

        else:
            action_response = -1 
            action_log += (f"({datetime.now()}) ERROR SOLO AHK: SOLOSoft.exe is already running. Please shutdown and try again.\n{error_msg}\n")

    except Exception as error_msg: 
        action_response = -1 
        action_log += (f"({datetime.now()}) ERROR SOLO CLIENT: Could not run soloRun method.\n{error_msg}\n")
        
    finally: 
        # format return dict
        return_dict = {
            'action_response': action_response,
            'action_msg': action_msg,
            'action_log': action_log
        }

        return return_dict



# Helper methods ------------------------------------------------------------------
def solo_already_running() -> bool: 
    is_already_running = False
    f = wmi.WMI()
    for process in f.Win32_Process():
        if process.Name == "SOLOSoft.exe":
            is_already_running = True 
    return is_already_running


# soloRun("C:\\Users\\svcaibio\\Dev\\hidex_module\\hidex_driver\\ahk\\test_hso\\test.hso")