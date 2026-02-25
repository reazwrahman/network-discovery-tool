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


def run_arp_via_sudo(iface, return_hosts=False):
    script_path = os.path.join(os.path.dirname(__file__), "arp.py")
    python_exec = sys.executable or "python3"
    print("Running ARP scan with sudo. You may be prompted for your admin password...")
    cmd = ["sudo", python_exec, script_path, "--iface-name", iface["name"], "--iface-ip", iface["ipv4"], "--netmask", iface["netmask"]]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError as e:
        print("Failed to run command:", e, file=sys.stderr)
        return [] if return_hosts else None

    hosts = []
    if proc.stdout:
        try:
            data = json.loads(proc.stdout)
            if isinstance(data, list):
                hosts = [h.get("ip") for h in data if isinstance(h, dict) and h.get("ip")]
        except Exception:
            print(proc.stdout)

    if proc.stderr:
        print(proc.stderr, file=sys.stderr)

    if return_hosts:
        return hosts


def run_ping_sweep_local(iface, return_hosts=False):
    # import here to avoid side effects at module import time
    import ping_sweep
    if not iface.get("ipv4") or not iface.get("netmask"):
        print("Interface missing IP/netmask; cannot run ping sweep.")
        return [] if return_hosts else None
    print(f"Running ping sweep for {iface['ipv4']}/{iface['netmask']}...")
    hosts = ping_sweep.run_ping_sweep(iface["ipv4"], iface["netmask"])
    for i, h in enumerate(hosts):
        print(f"[{i}] {h}")
    if return_hosts:
        return hosts

def run_mdns_discovery_local(iface):
    # import here to avoid side-effects at module import time
    import asyncio
    import dns_discovery
    if not iface.get("ipv4"):
        print("Interface missing IP; cannot run mDNS discovery.")
        return
    print(f"Running mDNS discovery on {iface['ipv4']}...")
    asyncio.run(dns_discovery.run_mdns_discovery(iface["ipv4"], duration_sec=10))


def run_port_scan_interactive(iface):
    """Ask user to pick a discovery method (ARP or ping sweep) to get IPs, then scan them."""
    import port_scanner
    
    print("\nChoose discovery method to get hosts for port scanning:")
    print(" 1) ARP discovery (requires sudo)")
    print(" 2) Ping sweep")
    
    while True:
        choice = input("Pick (1/2, q to cancel): ").strip()
        if choice.lower() in ("q", "quit", "exit"):
            print("Port scan cancelled.")
            return
        if choice == "1":
            hosts = run_arp_via_sudo(iface, return_hosts=True)
            break
        elif choice == "2":
            hosts = run_ping_sweep_local(iface, return_hosts=True)
            break
        else:
            print("Please enter 1 or 2.")
    
    if not hosts:
        print("No hosts discovered. Aborting port scan.")
        return
    
    print(f"\nDiscovered {len(hosts)} host(s): {hosts}")
    print(f"Scanning ports on {len(hosts)} host(s)...")
    results = port_scanner.run_port_scan(hosts)
    
    if not results:
        print("No results.")
        return
    for ip, ports in results.items():
        if ports:
            print(f"\n{ip}: Open ports: {ports}")
        else:
            print(f"\n{ip}: No open ports detected.")

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
    print("\nActions:\n 1) ARP discovery (requires sudo/admin password)\n 2) Ping sweep\n 3) mDNS/Zeroconf discovery\n 4) Port scanner")
    while True:
        choice = input("Pick action (1/2/3/4, q to quit): ").strip()
        if choice.lower() in ("q", "quit", "exit"):
            print("Cancelled.")
            return
        if choice == "1":
            run_arp_via_sudo(selected)
            return
        if choice == "2":
            run_ping_sweep_local(selected)
            return
        if choice == "3":
            run_mdns_discovery_local(selected)
            return
        if choice == "4":
            run_port_scan_interactive(selected)
            return
        print("Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
