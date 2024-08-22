#!/usr/bin/python3.9
import os

BYTES_SENT_THRESHOLD = 1500

BYTES_RECV_THRESHOLD = 1500


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
        print(f"Error fetching network stats: {e}")
        return None

def check_network_io_stats():
    network_io_stats = get_network_io_stats()

    if network_io_stats is None:
        return

    for interface, stats in network_io_stats.items():
        if stats['bytes_sent'] > BYTES_SENT_THRESHOLD * 1024**2:
            print(f"Warning: High network bytes sent on interface {interface}. Current usage: {stats['bytes_sent'] / (1024 ** 2):.2f} MB")
        if stats['bytes_recv'] > BYTES_RECV_THRESHOLD * 1024**2:
            print(f"Warning: High network bytes received on interface {interface}. Current usage: {stats['bytes_recv'] / (1024 ** 2):.2f} MB")

if __name__ == "__main__":
    check_network_io_stats()
