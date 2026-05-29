#!/usr/bin/env python3
"""Simple UDP listener for ASTERIX test traffic on port 8600."""

import socket

PORT = 8600

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))
print(f"Listening on UDP {PORT}...", flush=True)

while True:
    data, addr = sock.recvfrom(4096)
    print(f"{addr}: {data.hex().upper()}", flush=True)
