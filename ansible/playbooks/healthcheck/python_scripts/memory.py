#!/usr/bin/python3.9
import os


MEMORY_THRESHOLD = 80    
SWAP_THRESHOLD = 80      


def get_memory_info():
    with open('/proc/meminfo') as mem_file:
        mem_info = mem_file.readlines()

    total_mem = int(mem_info[0].split()[1]) / (1024 ** 2)   
    free_mem = int(mem_info[1].split()[1]) / (1024 ** 2)  
    used_mem = total_mem - free_mem
    mem_percent = (used_mem / total_mem) * 100

    if mem_percent > MEMORY_THRESHOLD:
        print("Memory Usage is over normal:")
        print(f"Total Memory: {total_mem:.2f} GB")
        print(f"Used Memory: {used_mem:.2f} GB")
        print(f"Memory Percent: {mem_percent:.2f}%")
    else:
        print("Memory Usage is normal.")
    

    with open('/proc/swaps') as swap_file:
        swap_info = swap_file.readlines()
    print("\n")
    for line in swap_info[1:]:
        swap_data = line.split()
        if len(swap_data) >= 5:
            total_swap = int(swap_data[2]) / (1024 ** 2)  
            used_swap = int(swap_data[3]) / (1024 ** 2)   
            swap_percent = (used_swap / total_swap) * 100

            if swap_percent > SWAP_THRESHOLD:
                print("\nSwap Usage is over normal:")
                print(f"Total Swap: {total_swap:.2f} GB")
                print(f"Used Swap: {used_swap:.2f} GB")
                print(f"Swap Percent: {swap_percent:.2f}%")
                break
            else:
                print(f"Swap usage is NORMAL {swap_percent:.2f}%")


if __name__ == "__main__":
    get_memory_info()
