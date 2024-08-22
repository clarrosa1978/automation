#!/usr/bin/python3.9
import os

log_files = ["/var/log/messages", "/var/log/secure", "/var/log/multipath", "/var/log/oracle.log"]
log_levels = ['WARNING', 'ERROR', 'CRITICAL']


def analyze_system_logs(log_files, log_levels, max_lines=20, max_line_length=100):
    for log_file in log_files:
        if not os.path.exists(log_file):
            print(f"File '{log_file}' not found. Errors not checked.")
            continue

        
        errors_found = False
        with open(log_file, 'r') as file:
            line_count = 0
            for line in file:
                for log_level in log_levels:
                    if log_level in line:
                        if len(line) > max_line_length:
                            print(f"{line[:max_line_length]}... (truncated)")
                        else:
                            print(line.strip())
                        line_count += 1
                        errors_found = True
                        break
                if line_count >= max_lines:
                    break
            if not errors_found:
                print( f"File '{log_file}': No errors found.")
        


if __name__ == "__main__":
    analyze_system_logs(log_files, log_levels)
    print("\n")
