import sys
import os
import time
from datetime import datetime

from ahk import AHK
from ahk.window import Window

def hidexOpenClose(): 
    """AHK script to open or close the Hidex drawer. NOTE: always start any protocol without the Hidex app open"""

    action_log = ""
    ahk = AHK()
    
    # open the Hidex app
    os.system('start C:\hidex\PlateReaderSoftware_Automation_1.3.1-rc\PlateReaderSoftware.exe') 
    time.sleep(5) # wait for window to open fully
    
    if ahk.pixel_get_color(1824,76) != '0xFFFFFF':  

        try:  
            # try to find the pop up window
            pre_release_pop_up = ahk.find_window(title=b'Internal pre-release version')

            # close the pop up if found
            if pre_release_pop_up.active:
                pre_release_pop_up.close()

                # wait for Hidex to initialize
                while ahk.pixel_get_color(1824,76) != '0xFFFFFF': 
                    action_log += (f"{datetime.now()} AHK: Waiting for hidex to initialize\n") 
                    time.sleep(1)
                time.sleep(.5)

        except Exception as error_msg: 
            action_log += (f"{datetime.now()} AHK: No initial pop up window found\n")
            action_log += (f"{datetime.now()} AHK: {error_msg}\n")

    # click open/close door button
    ahk.click(1824,76) 

    # return to main assay screen once complete 
    time.sleep(.5)
    ahk.click(36,168) 

    # minimize the hidex app after protcol complete
    time.sleep(.5) 
    main_hidex_window = Window.from_mouse_position(ahk)
    main_hidex_window.minimize()

    action_response = 0
    action_log += (f"{datetime.now()} AHK: Action complete, hidex opened/closed\n")

    # format return_dict
    return_dict = {
        'action_response': action_response,
        'action_log': action_log,
    }

    return return_dict

