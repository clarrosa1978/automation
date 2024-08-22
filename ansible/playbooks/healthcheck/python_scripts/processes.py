#!/usr/bin/python3.9
import subprocess

#Configuro umbrales para alertar
cpu_threshold = 30
memory_threshold = 30

def get_process_info():
    try:
        result = subprocess.run(['ps', '-e', '-o', 'pid,%cpu,%mem,comm'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        output = result.stdout.strip().split('\n')[1:]

        process_info = []
        for line in output:
            parts = line.strip().split(maxsplit=3)
            pid = parts[0]
            name = parts[3]
            cpu_percent = float(parts[1]) if parts[1] != 'pause' else 0.0
            memory_percent = float(parts[2]) if parts[2] != 'pause' else 0.0
            process_info.append({'pid': pid, 'name': name, 'cpu_percent': cpu_percent, 'memory_percent': memory_percent})

        return process_info
    except Exception as e:
        print("Error:", e)
        return None

def monitor_processes():
    process_info = get_process_info()

    if process_info is None:
        print("Failed to retrieve process information.")
        return

    #Uso listas para almacenar resultados y luego poder filtrarlos
    cpu_output = []
    memory_output = []

    for proc in process_info:
        pid = proc['pid']
        name = proc['name']
        cpu_percent = proc['cpu_percent']
        memory_percent = proc['memory_percent']

        if cpu_percent > cpu_threshold:
            cpu_output.append((cpu_percent, f"High CPU Usage: Process {name} (PID: {pid}) is using {cpu_percent}% CPU."))
        if memory_percent > memory_threshold:
            memory_output.append((memory_percent, f"High Memory Usage: Process {name} (PID: {pid}) is using {memory_percent}% memory."))

    #Ordeno lista
    cpu_output.sort(reverse=True)
    for _, message in cpu_output:
        print(message)
 

    #Ordeno lista
    memory_output.sort(reverse=True)
    for _, message in memory_output:
        print(message)

    if not memory_output:
        print("NORMAL MEMORY USAGE: Memory usage is under the threshold.")


if __name__ == "__main__":
    monitor_processes()
