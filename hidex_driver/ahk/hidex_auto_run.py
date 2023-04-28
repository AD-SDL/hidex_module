import sys
import os
import time
from datetime import datetime
import shutil

from ahk import AHK
from ahk.window import Window


# Python script to run a Hidex protocol
def hidexRun(protocol_path): 

    # capture contents of hidex data folder before run
    before_run__data_contents = list_data_files() 
    is_complete = False
    action_log = ""

    # run the Hidex Protocol with AHK python script ------------------------
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
                    print(f"({datetime.now()})  AHK: Waiting for hidex to initialize") 
                    time.sleep(1)
                time.sleep(.5)

        except Exception as error_msg: 
            print(f"({datetime.now()}) AHK ERROR: hidexRun unable to close initial pop up window")
            print(error_msg)

    # move mouse over import assay template button
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
    ahk.click(1700,990)

    # wait for the protocol to finish
    while (ahk.pixel_get_color(1700,990)) == '0x000000':  # check that run now button pixels are black (green when run complete)
        print(f"({datetime.now()}) AHK: Hidex protocol is still running")
        time.sleep(1)
    
    # return to main assay screen once complete 
    print(f"({datetime.now()}) AHK: Hidex protocol complete, returning to main assay screen")
    time.sleep(.5)
    ahk.click(36,168)

    # minimize the hidex app after protcol complete
    time.sleep(.5) 
    main_hidex_window = Window.from_mouse_position(ahk)
    main_hidex_window.minimize()
    
    # end of ahk python actions -----------------------------------------
    
    
    # capture contents of hidex data folder after the run 
    after_run_data_contents = list_data_files()

    # find data file added from this run 
    new_data_files = [f for f in after_run_data_contents if f not in before_run__data_contents]

    # make sure one data file captured, not > 1 or 0
    if len(new_data_files) == 1: 
        
        # TESTING
        print("one data file found")
        print(new_data_files) 

        new_data_path = new_data_files[0]
        
        action_response = 0
        action_msg = new_data_files[0]

    else: 
        
        # TESTING
        print("more than one data file found!")
        print(new_data_files)
        action_response = -1
        action_msg = new_data_files
        

#   # format return dict 
#     return_dict = {
#         'action_response': action_response,
#         'action_msg': action_msg,
#             'action_log': action_log,
#         }  

    is_complete = True
    print(f"({datetime.now()}) AHK: Returning True, hidex run completed")

    return is_complete
    # TODO: also return every message in one single string
    # TODO: action response  = 0 or 1
    # return_dict = {
    #     'action_response': is_complete, #int16 --> 1 if complete and some other number if an error maybe
    #     'action_msg': something_meaninful, (filename of new data)
    #     'action_log': string_of_logs
    # }
#hidexRun("C:\\Users\\svcaibio\\Documents\\Hidex Sense\\Campaign1_noIncubate2.sensetemplate")


# HELPER METHODS -----------------------------------------------
def list_data_files(hidex_data_folder = "C://labautomation//data_wei//one_file") -> list: 

    try: 
        # check that directory exists
        assert os.path.isdir(hidex_data_folder)

        current_data_files = [f for f in os.listdir(hidex_data_folder) if not os.path.isdir(f)]
        
        return current_data_files

    except AssertionError as assertion_error_msg: 
        print("ERROR: Hidex data folder on hudson01 cannot be found")
        print(assertion_error_msg)

    except Exception as error_msg: 
        print("ERROR: Cannot return files from hidex data folder")
        print(error_msg)


def archive_data(new_file_path, archive_folder = "C:\\labautomation\\data_wei\\proc") -> str:
    
    try: 
        file_name = os.path.basename(new_file_path)

        if os.isdir(archive_folder):
            archive_path = os.path.join(archive_folder, new_file_path)

            shutil.move(new_file_path, archive_path)
            
            # TESTING
            print("file has been moved!")

            return archive_path

        else: 
            print("ERROR: proc folder does not exist, cannot return new data file path")
            return None

    except Exception as error_msg: 
        print(error_msg)

        
    

