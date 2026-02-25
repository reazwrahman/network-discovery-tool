import psutil
import socket

def get_interfaces():
    interfaces = []
    raw_interfaces = psutil.net_if_addrs().items()

    for name, addrs in raw_interfaces:
        iface = {
            "name": name,
            "ipv4": None,
            "netmask": None,
            "mac": None
        }

        for addr in addrs:
            # IPv4
            if addr.family == socket.AF_INET:
                iface["ipv4"] = addr.address
                iface["netmask"] = addr.netmask

            # MAC address
            elif addr.family == psutil.AF_LINK:
                iface["mac"] = addr.address

        # Skip loopback or interfaces without IP and test if we can bind a socket to this IP
        if iface["ipv4"] and "lo" not in iface["name"]:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.bind((iface["ipv4"], 0))  # ephemeral port
                s.close()
                interfaces.append(iface)
            except OSError:
                # Skip interfaces that can’t be used
                pass

    return interfaces


def list_interfaces(ifaces):
    if not ifaces:
        print("No usable interfaces found.")
        return
    for i, iface in enumerate(ifaces):
        print("The following network interfaces were discovered: ")
        print(f"[{i}] {iface['name']}  IP: {iface['ipv4']}  Netmask: {iface['netmask']}  MAC: {iface.get('mac')}")



if __name__ == "__main__":
    for i, iface in enumerate(get_interfaces()):
        print(f"[{i}] {iface['name']}")
        print(f"     IP: {iface['ipv4']}")
        print(f"     Netmask: {iface['netmask']}")
        print(f"     MAC: {iface['mac']}")