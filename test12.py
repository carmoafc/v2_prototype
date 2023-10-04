import os
from datetime import datetime
import time

MAX_FILE_SIZE_B = 1024

def log_current_time(log_path):
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')               # ex: '2021-10-28_16-59-59'
    write_mode = 'a'                                            # assume we're going to append to the output file

    if os.path.isfile(log_path):                                # if the output file already exists
        size = os.path.getsize(log_path)                        # get file size in bytes
        if size >= MAX_FILE_SIZE_B:                             # if the file is too large, overwrite it entirely
            write_mode = 'w'

    with open(log_path, mode=write_mode) as output_file:
        output_file.write(timestamp + '\n')
        print(timestamp)

if __name__ == '__main__':
    log_path = '/home/pi/v2_prototype/output.txt'

    i = 0
    while i<10:
        log_current_time(log_path)
        time.sleep(1.0)
        i = i + 1
