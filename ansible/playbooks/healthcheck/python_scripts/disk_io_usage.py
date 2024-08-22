#!/usr/bin/python3.9

import psutil


def is_in_percentage_range(value, lower, upper):
    return int(value * 100) in range(int(lower * 100), int((upper + 1) * 100))

def get_disk_io_usage():
    print("Filesystem I/O check:\n")
    disk_io = psutil.disk_io_counters(perdisk=False)
    total_io = disk_io.read_count + disk_io.write_count
    total_time = disk_io.read_time + disk_io.write_time
    if total_time == 0:
        return 0
    io_percentage = (total_io / total_time) * 100
    

    IO_NORMAL = is_in_percentage_range(io_percentage, 0, 30)
    IO_HIGH = is_in_percentage_range(io_percentage, 30, 70)
    IO_CRITICAL = is_in_percentage_range(io_percentage, 70, 100)
        
    if IO_NORMAL:
        print("Disk I/O is NORMAL: {:.2f}%\n".format(io_percentage))                         
    elif IO_HIGH:
        print("Disk I/O is HIGH: {:.2f}%\n".format(io_percentage))
    elif IO_CRITICAL:
        print("Disk I/O is CRITICAL: {:.2f}%\n".format(io_percentage))
    else:
        print("Disk I/O : {:.2f}%\n".format(io_percentage))
    print()


        

if __name__ == "__main__":
    get_disk_io_usage()
