from msilib.schema import Directory
import sys
import os
import time
from datetime import datetime

from ahk import AHK
from ahk.window import Window



def list_data_files(hidex_data_folder) -> list: 

    
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



