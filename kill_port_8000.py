#!/usr/bin/env python3
"""
Kill process using port 8000
"""

import subprocess
import sys

def kill_port_8000():
    """Kill process using port 8000"""
    try:
        # Find process using port 8000
        result = subprocess.run(
            ["netstat", "-ano", "|", "findstr", ":8000"],
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            for line in lines:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    print(f"Found process using port 8000: PID {pid}")
                    
                    # Kill the process
                    kill_result = subprocess.run(
                        ["taskkill", "/PID", pid, "/F"],
                        capture_output=True,
                        text=True
                    )
                    
                    if kill_result.returncode == 0:
                        print(f"Successfully killed process {pid}")
                    else:
                        print(f"Failed to kill process {pid}: {kill_result.stderr}")
        else:
            print("No process found using port 8000")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    kill_port_8000()
