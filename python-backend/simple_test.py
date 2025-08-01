#!/usr/bin/env python3
import socket

# Test basic socket functionality
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.bind(('localhost', 8004))
    print("✅ Socket bind successful on port 8004")
    sock.listen(1)
    print("✅ Socket listen successful")
    sock.close()
    print("✅ Socket closed successfully")
except Exception as e:
    print(f"❌ Socket error: {e}")