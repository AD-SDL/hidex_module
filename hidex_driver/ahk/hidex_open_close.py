import sys
import os
import time

from ahk import AHK
from ahk.window import Window


def hidexOpenClose(): 
    """AHK script to open or close the Hidex drawer. NOTE: always start any protocol without the Hidex app open"""
 
    ahk = AHK()
    
    # TODO: could check system to see if Hidex program is already running
    # open the Hidex app
    os.system('start C:\hidex\PlateReaderSoftware_Automation_1.3.1-rc\PlateReaderSoftware.exe') 
    time.sleep(5) # wait for window to open fully

    if ahk.pixel_get_color(2495,75) != '0xFFFFFF':

        try:  
            # try to find the pop up window
            #pre_release_pop_up = ahk.win_wait(title=b'Internal pre-release version', timeout=5) # DOESN'T WORK
            pre_release_pop_up = ahk.find_window(title=b'Internal pre-release version')

            # close the pop up if found
            if pre_release_pop_up.active:
                pre_release_pop_up.close()

                # wait for Hidex to initialize
                while ahk.pixel_get_color(2495,75) != '0xFFFFFF':
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

    # move mouse over import assay template button
    ahk.mouse_move(2470, 81)
    ahk.click()

    # minimize the hidex app after protcol complete
    time.sleep(.5) # not necessary, but for demo
    main_hidex_window = Window.from_mouse_position(ahk)
    main_hidex_window.minimize()

hidexOpenClose()