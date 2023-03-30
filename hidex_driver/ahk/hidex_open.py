import sys
import os
import time

from ahk import AHK


# Python script to run a Hidex protocol
def hidexOpen(): 

    ahk = AHK()
    
    # open the Hidex app
    os.system('start C:\hidex\PlateReaderSoftware_Automation_1.3.1-rc\PlateReaderSoftware.exe') 

    # bring hidex window to the front

    # if 'Internal pre-release version' window appears 
    time.sleep(5)

    try: 
        # try to find the pop up window 
        #pre_release_pop_up = ahk.win_wait(title=b'Internal pre-release version', timeout=5) # DOESN'T WORK
        pre_release_pop_up = ahk.find_window(title=b'Internal pre-release version')

        # close the pop up if found
        if pre_release_pop_up.active:
            pre_release_pop_up.close()

            # wait for hidex to initialize
            time.sleep(21)

    except Exception as error_msg: 
        print("No initial pop up window found")

    try: 
        # look for the open close button on the screen
        print(ahk.image_search('C:\\Users\\svcaibio\\Dev\\hidex_module\\hidex_driver\\ahk\\images\\drawer_control.jpg'))
    
    except Exception as error_msg:
        print(error_msg)

    # # move mouse over import assay template button
    # ahk.mouse_move(2085, 329)
    # ahk.click()

    # time.sleep(1)
    # # for window in ahk.windows():
    # #     print(window.title)
    # # find the new window
    # try: 
    #     # locate the window
    #     import_template_pop_up = ahk.find_window(title=b'Import Template From File')

    #     # type in the path to template
    #     ahk.type(protocol_path)

    #     ahk.key_press('Enter')
    # except Exception as error_msg: 
    #     print(error_msg)



    # # while True: 
    # #     print(ahk.mouse_position)

hidexOpen()