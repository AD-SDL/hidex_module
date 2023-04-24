import sys
import os
import time

from ahk import AHK
from ahk.window import Window


def hidexOpenClose(): 
    """AHK script to open or close the Hidex drawer. NOTE: always start any protocol without the Hidex app open"""
    
    is_complete = False
    ahk = AHK()
    
    # TODO: could check system to see if Hidex program is already running
    # open the Hidex app
    os.system('start C:\hidex\PlateReaderSoftware_Automation_1.3.1-rc\PlateReaderSoftware.exe') 
    time.sleep(5) # wait for window to open fully
    
    if ahk.pixel_get_color(1824,76) != '0xFFFFFF':  # (2495,75) old HDMI coordinate

        try:  
            # try to find the pop up window
            pre_release_pop_up = ahk.find_window(title=b'Internal pre-release version')

            # close the pop up if found
            if pre_release_pop_up.active:
                pre_release_pop_up.close()

                # wait for Hidex to initialize
                while ahk.pixel_get_color(1824,76) != '0xFFFFFF':  # (2495,75) old HDMI coordinates
                    print("Waiting for hidex to initialize") 
                    time.sleep(1)
                time.sleep(.5)

        except Exception as error_msg: 
            print("No initial pop up window found")

    try: 
        # look for the open close button on the screen
        print(ahk.image_search('C:\\Users\\svcaibio\\Dev\\hidex_module\\hidex_driver\\ahk\\images\\drawer_control.jpg'))
    
    except Exception as error_msg:
        print(error_msg)

    # click open/close door button

    ahk.click(1824,76)  # (2470, 81) old HDMI coordinates

    # return to main assay screen once complete 
    print("Action complete: returning to main assay screen")
    time.sleep(.5)
    ahk.click(36,168)  # (36,168)  # old HDMI coordinates


    # minimize the hidex app after protcol complete
    time.sleep(.5) # not necessary, but for demo
    main_hidex_window = Window.from_mouse_position(ahk)
    main_hidex_window.minimize()

    is_complete = True 
    print("hidex opened/closed, returning True")

    return is_complete

