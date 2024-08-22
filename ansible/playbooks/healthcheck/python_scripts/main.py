#!/usr/bin/python3.9

import os
import psutil
import subprocess
import datetime
import socket
import time


# Variables
log_files = ["/var/log/messages", "/var/log/secure", "/var/log/multipath", "/var/log/oracle.log"]
log_levels = ['WARNING', 'ERROR', 'CRITICAL']
MEMORY_THRESHOLD = 80
SWAP_THRESHOLD = 80
BYTES_SENT_THRESHOLD = 1500
BYTES_RECV_THRESHOLD = 1500
PROCESS_CPU_THRESHOLD = 30
PROCESS_MEMORY_THRESHOLD = 30
output_file = "/tmp/monitoring_output.txt"


def get_hostname():
    hostname = socket.gethostname()
    with open(output_file, "w") as f:
        f.write("\n\n")
        f.write(f"###################################################################### {hostname} ######################################################################\n\n")
        f.write("\n\n")

# Helper function
def is_in_percentage_range(value, min_percentage, max_percentage):
    return min_percentage < value <= max_percentage

##v2
def check_disk_usage():
    with open(output_file, "a") as f:
        partitions = psutil.disk_partitions(all=False)
        fs_alertados = []
        for partition in partitions:
            if not partition.device.startswith('/dev/'):
                continue
            usage = psutil.disk_usage(partition.mountpoint)
            percent_used = usage.percent

            FS_WARNING = is_in_percentage_range(percent_used, 80, 85)
            FS_HIGH = is_in_percentage_range(percent_used, 85, 90)
            FS_CRITICAL = is_in_percentage_range(percent_used, 90, 100)
            if FS_WARNING:
                fs_alertados.append("{} - {}% used |  WARNING".format(partition.mountpoint, percent_used))
            elif FS_HIGH:
                fs_alertados.append("{} - {}% used | HIGH".format(partition.mountpoint, percent_used))
            elif FS_CRITICAL:
                fs_alertados.append("{} - {}% used | CRITICAL".format(partition.mountpoint, percent_used))
        if fs_alertados:
          f.write("\n")
          f.write("*****Filesystems alertados*****\n\n")

        f.write("\n".join(fs_alertados) + "\n\n")


##v2
def get_disk_io_usage(interval=10):
    with open(output_file, "a") as f:
        disk_io_start = psutil.disk_io_counters()
        time.sleep(interval)
        disk_io_end = psutil.disk_io_counters()
        read_bytes = disk_io_end.read_bytes - disk_io_start.read_bytes
        write_bytes = disk_io_end.write_bytes - disk_io_start.write_bytes
        total_bytes = read_bytes + write_bytes
        total_time = interval
        io_percentage = int((total_bytes / total_time) * 100 / psutil.disk_usage('/').total)

        IO_NORMAL = is_in_percentage_range(io_percentage, -1, 30)
        IO_HIGH = is_in_percentage_range(io_percentage, 31, 70)
        IO_CRITICAL = is_in_percentage_range(io_percentage, 71, 100)

        if IO_HIGH:
            f.write("#####I/O disco alertado#####\n")
            f.write("\n")
            f.write("Disk I/O está ALTO: {:.2f}%\n".format(io_percentage))
        elif IO_CRITICAL:
            f.write("#####I/O disco alertado#####\n")
            f.write("\n")
            f.write("Disk I/O está CRITICO: {:.2f}%\n".format(io_percentage))

        f.write("\n")


#v2
def analyze_system_logs(log_files, log_levels, max_lines=20, max_line_length=100):
    with open(output_file, "a") as f:
        errors_found_global = False
        for log_file in log_files:
            if not os.path.exists(log_file):
                continue
            errors_found_local = False
            with open(log_file, 'r') as file:
                line_count = 0
                for line in file:
                    for log_level in log_levels:
                        if log_level in line:
                            if not errors_found_global:
                                f.write("\n")
                                f.write("#####LOGS CON ERRORES#####\n\n")
                                errors_found_global = True
                            if not errors_found_local:
                                f.write("\n")
                                f.write(f"Archivo '{log_file}':\n\n")
                                errors_found_local = True
                            if len(line) > max_line_length:
                                f.write(f"{line[:max_line_length]}... (truncated)\n")
                            else:
                                f.write(line.strip() + "\n")
                            line_count += 1
                            break
                    if line_count >= max_lines:
                        break

                if not errors_found_local:
                    continue



# Function to get memory information
def get_memory_info():
    with open(output_file, "a") as f:
        mem = psutil.virtual_memory()
        total_mem = mem.total / (1024 ** 3)
        free_mem = mem.available / (1024 ** 3)
        used_mem = total_mem - free_mem
        mem_percent = (used_mem / total_mem) * 100
        if mem_percent > MEMORY_THRESHOLD:
            f.write("\n")
            f.write("*****Memoria RAM alertada*****\n\n")
            f.write("\n")
            f.write(f"Memoria total: {total_mem:.2f} GB\n")
            f.write(f"Memoria usada: {used_mem:.2f} GB\n")
            f.write(f"Porcentaje memoria: {mem_percent:.2f}%\n\n")
        swap = psutil.swap_memory()
        total_swap = swap.total / (1024 ** 3)
        used_swap = swap.used / (1024 ** 3)
        swap_percent = (used_swap / total_swap) * 100
        if swap_percent > SWAP_THRESHOLD:
            f.write("*****Swap alertado*****\n\n")
            f.write("\n")
            f.write(f"Swap total: {total_swap:.2f} GB\n")
            f.write(f"Swap usado: {used_swap:.2f} GB\n")
            f.write(f"Porcentaje Swap: {swap_percent:.2f}%\n\n")

        





# Function to get network I/O stats
def get_network_io_stats():
    try:
        with open('/proc/net/dev', 'r') as f:
            lines = f.readlines()
        stats = {}
        for line in lines[2:]:
            fields = line.split()
            interface = fields[0].replace(":", "")
            if interface != 'lo':
                bytes_recv = int(fields[1])
                bytes_sent = int(fields[9])
                stats[interface] = {'bytes_sent': bytes_sent, 'bytes_recv': bytes_recv}
        return stats
    except Exception as e:
        with open(output_file, "a") as f:
            f.write(f"Error fetching network stats: {e}\n")
        return None

# Function to check network I/O stats
def check_network_io_stats():
    with open(output_file, "a") as f:
        f.write("\n")
        f.write("#####NETWORK#####\n")
        f.write("\n")
        network_io_stats = get_network_io_stats()
        if network_io_stats is None:
            return
        for interface, stats in network_io_stats.items():
            network_warning = False
            if stats['bytes_sent'] > BYTES_SENT_THRESHOLD * 1024**2:
                if not network_warning:
                    network_warning = True
                    f.write(f"Warning: High network bytes sent on interface {interface}. Current usage: {stats['bytes_sent'] / (1024 ** 2):.2f} MB\n")                
            if stats['bytes_recv'] > BYTES_RECV_THRESHOLD * 1024**2:
                if not network_warning:
                    network_warning = True
                    f.write(f"Warning: High network bytes received on interface {interface}. Current usage: {stats['bytes_recv'] / (1024 ** 2):.2f} MB\n")
        f.write("\n")

# Function to get process information
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
        with open(output_file, "a") as f:
            f.write(f"Error: {e}\n")
        return None

#v2
def monitor_processes():
    with open(output_file, "a") as f:
        f.write("\n")
        f.write("\n")
        process_info = get_process_info()
        if process_info is None:
            f.write("No se pudo obtener información.\n")
            return
        cpu_output = []
        memory_output = []
        for proc in process_info:
            procesos_alertados = False
            pid = proc['pid']
            name = proc['name']
            cpu_percent = proc['cpu_percent']
            memory_percent = proc['memory_percent']
            if cpu_percent > PROCESS_CPU_THRESHOLD:
                if not procesos_alertados:
                   f.write("#####Procesos alertados por CPU#####\n")
                   f.write("\n")
                   procesos_alertados = True
                   cpu_output.append((cpu_percent, f"Uso de CPU alto: Proceso {name} (PID: {pid}) está usando {cpu_percent}% de CPU."))
            if memory_percent > PROCESS_MEMORY_THRESHOLD:
                if not procesos_alertados:
                   f.write("#####Procesos alertados por memoria#####\n")
                   f.write("\n")
                   procesos_alertados = True
                   memory_output.append((memory_percent, f"Uso de Memoria alto: Proceso {name} (PID: {pid}) está usando {memory_percent}% de memoria."))
        cpu_output.sort(reverse=True)
        for _, message in cpu_output:
            f.write(message + "\n")
        memory_output.sort(reverse=True)
        for _, message in memory_output:
            f.write(message + "\n")

         

#v2
def check_enabled_and_running_services():
    with open(output_file, "a") as f:
        redhat_version = subprocess.getoutput("cat /etc/redhat-release")

        enabled_services_command = " "
        if "release 6" in redhat_version:
            enabled_services_command = "chkconfig --list | grep '3:on' | awk '{print $1}'"
        elif "release 7" in redhat_version\
             or "release 8" in redhat_version\
              or "release 9" in redhat_version:
            enabled_services_command = " systemctl list-unit-files --type=service | grep enabled |\
                                          grep '.service' | awk '{print $1}'asd"

        enabled_services_output = subprocess.check_output(enabled_services_command, shell=True,\
                                    universal_newlines=True)
        enabled_services = enabled_services_output.strip().split('\n')

        service_exceptions = {'sysstat','bmc-watchdog','kdump', 'certmonger', 'abrt-ccpp', 'blk-availability', \
                              'cpuspeed', 'dhcpd', 'firstboot', 'ipmi', 'ipmidetectd',\
                              'iptables', 'iscsi', 'iscsid', 'lvm2-monitor', 'mdmonitor',\
                              'netfs', 'network', 'osad', 'portreserve', 'rpcgssd',\
                              'udev-post'}
        status_command = ""

        if "release 6" in redhat_version:
            status_command = "service {} status"
        elif any(version in redhat_version for version in ["release 7", "release 8", "release 9"]):
            status_command = "systemctl status {}"

        not_running_services = []
        for service in enabled_services:
            if not any(exception in service for exception in service_exceptions):
               status_output = subprocess.getoutput(status_command.format(service))
               if "running" not in status_output.lower():
                   not_running_services.append(service)
        if not_running_services:
            f.write(" \n")
            f.write("#####Servicios alertados#####\n\n")
            f.write(" \n")
            f.write("Algunos de los servicios habilitados no están en ejecución:\n\n")
            for service in not_running_services:
                f.write("- {}\n".format(service))
            f.write(" \n")

          


#v2
def sudoers_last_mod():
    with open(output_file, "a") as f:
        f.write("")
        sudoers_path = "/etc/sudoers"
        modification_time = os.path.getmtime(sudoers_path)
        modification_date = datetime.datetime.fromtimestamp(modification_time)
        current_date = datetime.datetime.now()
        time_difference = current_date - modification_date
        if time_difference.days < 5:
            f.write("")
            f.write("#####/etc/sudoers alertado#####\n\n")
            f.write("¡¡El archivo /etc/sudoers fue editado hace menos de 5 dias!!! [Warning]\n")
            f.write("")

#v2
def check_sudoers_syntax():
    try:
        result = subprocess.run(['visudo', '-c'] , capture_output=True, text=True, check=True)
        if result.returncode != 0:
            with open(output_file, "a") as f:
                f.write("Fallo el chequeo de syntax.\n")
                f.write(result.stdout + "\n\n")
    except subprocess.CalledProcessError as e:
        with open(output_file, "a") as f:
            f.write("*****Error al verificar sudoers*****\n\n")
            f.write("Fallo el chequeo de syntax.\n\n")

    
#v2
def check_multipath():
    with open(output_file, "a") as f:
        try:
            subprocess.check_output(["service", "multipathd", "status"], stderr=subprocess.DEVNULL)
            output = subprocess.check_output(["multipath", "-t"]).decode("utf-8")
            if "multipathd" in output:
                try:
                    output = subprocess.check_output(["multipath", "-ll"]).decode("utf-8")
                    failed_paths = []
                    lines = output.split('\n')
                    for line in lines:
                        if line.startswith("failed"):
                            failed_paths.append(line)
                    if failed_paths:
                        f.write("Paths fallidos: \n\n")
                        for path in failed_paths:
                            f.write(path + "\n")
                except subprocess.CalledProcessError:
                    f.write("#####Pasos de multipath alertados#####\n\n")
                    f.write("Hubo un error al chequear los paths fallidos.\n")
            else:
                f.write("Multipath está habilitado pero multipathd no está manejando ningún dispositivo.\n")
        except subprocess.CalledProcessError:
            f.write("\n")


if __name__ == "__main__":
    get_hostname()
    check_disk_usage()
    get_disk_io_usage()
    analyze_system_logs(log_files, log_levels)
    get_memory_info()
    #check_network_io_stats()
    monitor_processes()
    check_enabled_and_running_services()
    check_multipath()
    sudoers_last_mod()
    check_sudoers_syntax()
    

    print("Monitoring outputs written to", output_file)
