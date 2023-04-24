import sys
import os
import time

from ahk import AHK
from ahk.window import Window


# Python script to run a Hidex protocol
def hidexRun(protocol_path): 

    is_complete = False
    ahk = AHK()
    
    # open the Hidex app
    os.system('start C:\hidex\PlateReaderSoftware_Automation_1.3.1-rc\PlateReaderSoftware.exe') 
    time.sleep(5) # wait for window to open fully

    #if ahk.pixel_get_color(2495,75) != '0xFFFFFF':  # old HDMI coordinates
    if ahk.pixel_get_color(1824,76) != '0xFFFFFF':

        try:  
            # try to find the pop up window
            #pre_release_pop_up = ahk.win_wait(title=b'Internal pre-release version', timeout=5) # DOESN'T WORK
            pre_release_pop_up = ahk.find_window(title=b'Internal pre-release version')

            # close the pop up if found
            if pre_release_pop_up.active:
                pre_release_pop_up.close()

                # wait for Hidex to initialize
                #while ahk.pixel_get_color(2495,75) != '0xFFFFFF':  # old HDMI coordinates
                while ahk.pixel_get_color(1824,76) != '0xFFFFFF':
                    print("Waiting for hidex to initialize") 
                    time.sleep(1)
                time.sleep(.5)

        except Exception as error_msg: 
            print("No initial pop up window found")

    # move mouse over import assay template button
    # ahk.mouse_move(2085, 329)  # old HDMI coordinates
    # ahk.click()
    ahk.click(1765,318)
    time.sleep(1)
   
    try: 
        # locate the window
        import_template_pop_up = ahk.find_window(title=b'Import Template From File')

        if import_template_pop_up:
        # type in the path to template
            ahk.type(protocol_path)

            ahk.key_press('Enter')

    except Exception as error_msg: 
        print(error_msg)

    # run the imported protocol template file
    # ahk.mouse_move(2170,1354)  # old HDMI coordinates
    # ahk.click()
    ahk.click(1700,990)

    # wait for the protocol to finish
    #while (ahk.pixel_get_color(2324,1362)) == '0x000000': 
    while (ahk.pixel_get_color(1700,990)) == '0x000000':
        print("Hidex protocol is still running")
        print(ahk.pixel_get_color(1700,990))
        time.sleep(1)
    
    # return to main assay screen once complete 
    print("Hidex protocol complete, returning to main assay screen")
    time.sleep(.5)
    # ahk.mouse_move(36,168)  # old HDMI coordinates
    # ahk.click()
    ahk.click(36,168)

    # minimize the hidex app after protcol complete
    time.sleep(.5) # not necessary, but for demo
    main_hidex_window = Window.from_mouse_position(ahk)
    main_hidex_window.minimize()
    
    # TODO: return the name of the data file that was created
    is_complete = True
    print("Returning True: hidex run completed")

    return is_complete

#hidexRun("C:\\Users\\svcaibio\\Documents\\Hidex Sense\\Campaign1_noIncubate2.sensetemplate")
