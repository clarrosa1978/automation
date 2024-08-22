#!/usr/bin/python3.9

import subprocess
import os
import datetime


def sudoers_last_mod():
    sudoers_path = "/etc/sudoers"
    modification_time = os.path.getmtime(sudoers_path)
    modification_date = datetime.datetime.fromtimestamp(modification_time)

    current_date = datetime.datetime.now()
    time_difference = current_date - modification_date
    
    if time_difference.days < 5:
        print(f"¡¡Sudoers main file was modifies in the last 5 days!!")
    else:
        print(f"Sudoers main file was modified {time_difference.days} days ago... ")

def check_sudoers_syntax():
    try:
        result = subprocess.run(['visudo', '-c'] , capture_output=True, text=True, check=True)
        if result.returncode == 0:
            print("Sudoers files syntax is OK")
        else:
            print("Sudoers syntax check failed.")
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error running visudo ", e)



sudoers_last_mod()

check_sudoers_syntax()