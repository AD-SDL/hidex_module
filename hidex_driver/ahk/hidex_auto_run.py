import sys
import os
import time

from ahk import AHK


# Python script to run a Hidex protocol
def hidexRun(protocol_path): 

    ahk = AHK()
    
    # open the Hidex app
    os.system('start C:\hidex\PlateReaderSoftware_Automation_1.3.1-rc\PlateReaderSoftware.exe') 

    # find the hidex window and maximize it
    # TODO: How to find the Hidex window? always spin the node without the app running, the first time the app is opened it should be maximized. 

    # if 'Internal pre-release version' window appears 
    time.sleep(5)

    print("Initial printing of windows HERE")
    for window in ahk.windows():
        print(window.title)

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

    # move mouse over import assay template button
    ahk.mouse_move(2085, 329)
    ahk.click()

    time.sleep(1)
   
    try: 
        # locate the window
        import_template_pop_up = ahk.find_window(title=b'Import Template From File')

        # type in the path to template
        ahk.type(protocol_path)

        ahk.key_press('Enter')

    except Exception as error_msg: 
        print(error_msg)

    # run the imported protocol template file
    ahk.mouse_move(2170,1354)
    ahk.click()

    # wait for the protocol to finish
    time.sleep(1200)  # TODO: figure out how long to sleep for here. Is there a better way to check when the protocol is over

    # return to main screen after done (or before waiting?)


hidexRun("C:\\Users\\svcaibio\\Documents\\Hidex Sense\\Campaign1_noIncubate2.sensetemplate")