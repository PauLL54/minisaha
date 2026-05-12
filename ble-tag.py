#!/usr/bin/env python3
import subprocess
import re
import time
import sys
import re

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

def strip_ansi(s):
    return ansi_escape.sub('', s)

if len(sys.argv) < 2:
    print("Gebruik: ./bluetooth.py <speaker-naam>")
    sys.exit(1)

SPEAKER_NAME = sys.argv[1]
print(SPEAKER_NAME)

def main():
    # Start bluetoothctl met stdin+stdout als pipes
    proc = subprocess.Popen(
        ["bluetoothctl"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1  # line-buffered
    )

    def send(cmd):
        print(f">>> {cmd.strip()}")
        proc.stdin.write(cmd + "\n")
        proc.stdin.flush()

    # Basis setup
    send("power on")
    time.sleep(3)
    send("agent on")
    time.sleep(2)
    send("default-agent")
    time.sleep(2)
    send("scan on")
    time.sleep(2)

    print("Scanning... zet je speaker in PAIRING MODE")

    while True:
        line = proc.stdout.readline()
        if not line:
            print("bluetoothctl gestopt")
            # bluetoothctl gestopt
            break

        # verwijder kleurcodes
        clean = strip_ansi(line).strip()
        # voor Bookworm:
        clean = clean.replace('\x01', '').replace('\x02', '')
        print(f"BT: {clean}")

        # Zoek [NEW] Device ... regels
        match = re.search(r"\[NEW\] Device ([0-9A-F:]{17}) (.+)", clean)
        if match:
            mac = match.group(1)
            name = match.group(2).strip()
            print(f"Gevonden device: {mac} ({name})")
            if SPEAKER_NAME.lower() in name.lower():
                print("→ Dit is de speaker, pair/trust/connect...")

                send(f"pair {mac}")
                time.sleep(2)
                send(f"trust {mac}")
                time.sleep(2)
                send(f"connect {mac}")
                time.sleep(2)
                print("Klaar.")
                break

if __name__ == "__main__":
    main()

