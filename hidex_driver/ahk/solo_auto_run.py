import os
import sys
import wmi
import psutil
import time

from ahk import AHK
from ahk.window import Window


def soloRun(solo_hso_path):

    ahk = AHK()
    
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
            print("window = " + str(soloSoft_window))

            # make the window full screen
            soloSoft_window.maximize()

            # press 'Open File' button
            ahk.click(34,57)   # old HDMI coordinates: File = (14,32), Open = (25,76)

            # insert path of hso protocol 
            time.sleep(3)
            ahk.type(solo_hso_path)

            time.sleep(.5)
            ahk.key_press("Enter")

            # press run button then "Enter" to bypass the "Are you sure?" screen
            time.sleep(.5)
            ahk.mouse_move(195,59) #(193,59) old HDMI coordinates
            ahk.click()
            time.sleep(.5)
            ahk.key_press("Enter")
            

    #         # ---- SOLO program is now running! --------------

            # monitor for "Running Method..." or "Run Stopped" windows
            time.sleep(.5)
            while True: 
                try: 
                    run_completed_window = ahk.find_window(title=b'SOLOSoft',text=b'OK\r\nRun Completed.\r\n')
                    run_stopped_window = ahk.find_window(title=b'SOLOSoft',text=b'OK\r\nRun Stopped.\r\n')
                    still_running_window = ahk.find_window(title=b"Running Method...")

                    print("Run completed: " + str(True if run_completed_window else False))
                    print("Run stopped: " + str(True if run_stopped_window else False))
                    print("Still running: " + str(True if still_running_window else False))
                    print("----------------------------")

                except Exception as error_msg: 
                    print(error_msg)
                
                time.sleep(2)
                
                if still_running_window and not (run_stopped_window or run_completed_window): 
                    print("STATUS: hso running") 
                elif not still_running_window and run_stopped_window: 
                    print("STATUS: hso protocol stopped, see SoloSoft app for error details")
                    break
                elif not still_running_window and run_completed_window: 
                    print("STATUS: hso run completed")
                    time.sleep(1)

                    # close down the SOLOSoft app after the run
                    for proc in psutil.process_iter():
                        if proc.name() == "SOLOSoft.exe":
                            proc.kill()
                            print("SoftLinx shut down complete")
                    break
                else: 
                    print("STATUS: TODO: handle this intermediate state")

        except Exception as error_msg: 
            
            print(error_msg)
            

    # else:
    #     print("SOLOSoft.exe is already running. Please shutdown and try again")
    #     # TODO: could shut down SOLOSoft here but might not be a good idea if something important is already running


# Helper methods ------------------------------------------------------------------
def solo_already_running() -> bool: 
    is_already_running = False
    f = wmi.WMI()
    for process in f.Win32_Process():
        if process.Name == "SOLOSoft.exe":
            is_already_running = True 
    return is_already_running


soloRun("C:\\Users\\svcaibio\\Dev\\hidex_module\\hidex_driver\\ahk\\test_hso\\test.hso")