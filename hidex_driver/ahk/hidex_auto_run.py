import sys
import os
import time
from datetime import datetime
import shutil

from ahk import AHK
from ahk.window import Window


# Python script to run a Hidex protocol
def hidexRun(protocol_path): 

    action_log = ""

    # capture contents of hidex data folder before run
    before_run__data_contents, list_log = list_data_files() 
    action_log += list_log

    # run Hidex protocol in app with ahk python script 
    ahk_complete, ahk_log = run_protocol_ahk(protocol_path)
    action_log += ahk_log

    if ahk_complete == True: 
        # capture contents of hidex data folder after the run 
        after_run_data_contents, list_log = list_data_files()
        action_log += list_log

        # find data file added from this run 
        new_data_files = [f for f in after_run_data_contents if f not in before_run__data_contents]

        # ensure only one new data file found
        if len(new_data_files) == 1:  

            # move the file to proc folder 
            relocated_data_path, archive_log = archive_data(new_data_files[0])
            action_log += archive_log

            # format response message variables
            action_response = 0
            action_msg = relocated_data_path   

            # record in log
            action_log += (f"({datetime.now()}) CLIENT: one new hidex data file found, {relocated_data_path}\n")

        else: # if there are 0 or more than one new data file
            
            #  format response message variables
            action_response = -1
            action_msg = []
            
            # record in log
            action_log += (f"({datetime.now()}) ERROR CLIENT: {len(new_data_files)} hidex data files found, should be 1.\n")
            
    else: # if ahk did not complete 

        # format response message variables 
        action_response = -1
        action_msg = []

        # record in log
        action_log += (f"({datetime.now()}) ERROR CLIENT: Hidex ahk sequence did not complete.\n")

    # format return dict
    return_dict = {
        'action_response': action_response,
        'action_msg': action_msg,
        'action_log': action_log
    }

    return return_dict 


# HELPER METHODS -----------------------------------------------

def run_protocol_ahk(protocol): 
    """
    
    """
    ahk = AHK()
    ahk_log = ""
    ahk_complete = False 
    
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
                    ahk_log += (f"({datetime.now()})  AHK: Waiting for hidex to initialize\n") 
                    time.sleep(1)
                time.sleep(.5)

        except Exception as error_msg: 
            ahk_log += (f"({datetime.now()}) AHK ERROR: hidexRun unable to close initial pop up window\n")
            ahk_log += print(error_msg) + "\n"

    # move mouse over import assay template button
    ahk.click(1765,318)
    time.sleep(1)
   
    try: 
        # locate the window
        import_template_pop_up = ahk.find_window(title=b'Import Template From File')

        if import_template_pop_up:
        # type in the path to template
            ahk.type(protocol)

            ahk.key_press('Enter')

    except Exception as error_msg: 
        ahk_log += error_msg + "\n"

    # run the imported protocol template file
    ahk.click(1700,990)

    # wait for the protocol to finish
    while (ahk.pixel_get_color(1700,990)) == '0x000000':  # check that run now button pixels are black (green when run complete)
        ahk_log += (f"({datetime.now()}) AHK: Hidex protocol is still running\n")
        time.sleep(1)
    
    # return to main assay screen once complete 
    ahk_log += (f"({datetime.now()}) AHK: Hidex protocol complete, returning to main assay screen\n")
    time.sleep(.5)
    ahk.click(36,168)

    # minimize the hidex app after protocol complete
    time.sleep(.5) 
    try: 
        main_hidex_window = Window.from_mouse_position(ahk)
        main_hidex_window.minimize()
        ahk_complete = True

    except Exception as error_msg: 
        ahk_log += (f"({datetime.now()}) AHK ERROR: could not minimize main hidex window\n")
        ahk_log += error_msg + "\n"

    return ahk_complete, ahk_log
    


def list_data_files(hidex_data_folder = "C:\\labautomation\\data_wei\\one_file") -> list: 

    list_log = ""
    current_data_files = []

    try: 
        # check that directory exists
        assert os.path.isdir(hidex_data_folder)

        current_data_files = [os.path.abspath(os.path.join(hidex_data_folder,f)) for f in os.listdir(hidex_data_folder) if not os.path.isdir(f)]

    except AssertionError as assertion_error_msg: 
        list_log += (f"({datetime.now()}) ERROR: Hidex data folder on hudson01 cannot be found\n")
        list_log += (f"({datetime.now()}) {assertion_error_msg}\n")

    except Exception as error_msg: 
        list_log += (f"({datetime.now()}) ERROR: Cannot return files from hidex data folder\n")
        list_log += (f"({datetime.now()}) {error_msg}\n")

    return current_data_files, list_log



def archive_data(new_file_path, archive_folder = "C:\\labautomation\\data_wei\\proc") -> str:

    archive_log = ""
    archive_path = None
    
    try: 
        file_name = os.path.basename(new_file_path)

        if os.path.isdir(archive_folder):

            # format new path in proc folder
            archive_path = os.path.join(archive_folder, file_name)

            # move file to new location
            shutil.move(new_file_path, archive_path)

        else: 
            archive_log += (f"({datetime.now()}) ERROR: proc folder does not exist, cannot return new data file path\n")

    except Exception as error_msg: 
        archive_log += (f"({datetime.now()} {error_msg}\n")
        
    return archive_path, archive_log
    

        
    

