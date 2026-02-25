#!/usr/bin/env python3
import argparse
import sys
import os
import subprocess
import json
from network_interface import get_interfaces, list_interfaces


def select_interface_interactive(ifaces):
    list_interfaces(ifaces)
    if not ifaces:
        return None
    while True:
        try:
            choice = input("Select interface index to continue the discovery (q to quit): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return None

        if choice.lower() in ("q", "quit", "exit"):
            return None
        if not choice.isdigit():
            print("Please enter a number.")
            continue
        idx = int(choice)
        if 0 <= idx < len(ifaces):
            return ifaces[idx]
        print("Index out of range.")


def run_arp_via_sudo(iface):
    script_path = os.path.join(os.path.dirname(__file__), "arp.py")
    python_exec = sys.executable or "python3"
    cmd = ["sudo", python_exec, script_path, "--iface-name", iface["name"], "--iface-ip", iface["ipv4"], "--netmask", iface["netmask"]]
    print("Running ARP scan with sudo. You may be prompted for your admin password...")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError as e:
        print("Failed to run command:", e, file=sys.stderr)
        return

    if proc.stdout:
        try:
            data = json.loads(proc.stdout)
            if isinstance(data, list):
                for i, h in enumerate(data):
                    print(f"[{i}] {h}")
            else:
                print(proc.stdout)
        except Exception:
            print(proc.stdout)

    if proc.stderr:
        print(proc.stderr, file=sys.stderr)


def run_ping_sweep_local(iface):
    # import here to avoid side-effects at module import time
    import ping_sweep
    if not iface.get("ipv4") or not iface.get("netmask"):
        print("Interface missing IP/netmask; cannot run ping sweep.")
        return
    print(f"Running ping sweep for {iface['ipv4']}/{iface['netmask']}...")
    hosts = ping_sweep.run_ping_sweep(iface["ipv4"], iface["netmask"])
    for i, h in enumerate(hosts):
        print(f"[{i}] {h}")


def main():
    parser = argparse.ArgumentParser(description="Interactive network discovery CLI")
    parser.add_argument("--list", action="store_true", help="List interfaces and exit")
    parser.add_argument("--select", type=int, help="Non-interactive: select interface by index and print it")
    args = parser.parse_args()

    ifaces = get_interfaces()

    if args.list:
        list_interfaces(ifaces)
        return

    if args.select is not None:
        idx = args.select
        if 0 <= idx < len(ifaces):
            selected = ifaces[idx]
        else:
            print("Index out of range", file=sys.stderr)
            sys.exit(2)
    else:
        selected = select_interface_interactive(ifaces)

    if not selected:
        print("No selection made.")
        return

    print("Selected interface:", selected)

    # Action menu
    print("\nActions:\n 1) ARP discovery (requires sudo)\n 2) Ping sweep")
    while True:
        choice = input("Pick action (1/2, q to quit): ").strip()
        if choice.lower() in ("q", "quit", "exit"):
            print("Cancelled.")
            return
        if choice == "1":
            run_arp_via_sudo(selected)
            return
        if choice == "2":
            run_ping_sweep_local(selected)
            return
        print("Please enter 1 or 2.")


if __name__ == "__main__":
    main()
