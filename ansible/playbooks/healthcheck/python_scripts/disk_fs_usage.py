#!/usr/bin/python3.9

import psutil


def is_in_percentage_range(value, lower, upper):
    return int(value * 100) in range(int(lower * 100), int((upper + 1) * 100))


def check_disk_usage():
    print("Filesystem usage check:\n")
    issues_found = False
    partitions = psutil.disk_partitions(all=False)
    for partition in partitions:
        if not partition.device.startswith('/dev/'):
            continue
        usage = psutil.disk_usage(partition.mountpoint)
        percent_used = usage.percent
        
        FS_WARNING = is_in_percentage_range(percent_used, 80, 85)
        FS_HIGH = is_in_percentage_range(percent_used, 85, 90)
        FS_CRITICAL = is_in_percentage_range(percent_used, 90, 100)

        if FS_WARNING:
            print("{} - {}% used |  WARNING".format(partition.mountpoint, percent_used))
            issues_found = True
        elif FS_HIGH:
            print("{} - {}% used | HIGH".format(partition.mountpoint, percent_used))
            issues_found = True
        elif FS_CRITICAL:
            print("{} - {}% used | CRITICAL".format(partition.mountpoint, percent_used))
            issues_found = True
            
    if not issues_found:
        print("*** Filesystems are fine ***")
    print()

if __name__ == "__main__":
    check_disk_usage()
