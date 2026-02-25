from scapy.all import ARP, Ether, srp
import ipaddress


def arp_scan(iface_name, iface_ip, iface_netmask):
    network = ipaddress.IPv4Network(f"{iface_ip}/{iface_netmask}", strict=False)

    arp = ARP(pdst=str(network))
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    ans, _ = srp(packet, timeout=3, iface=iface_name, verbose=False)

    hosts = []
    for _, received in ans:
        hosts.append({"ip": received.psrc, "mac": received.hwsrc})

    return hosts


def _main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Run an ARP scan on a given interface.")
    parser.add_argument("--iface-name", required=True)
    parser.add_argument("--iface-ip", required=True)
    parser.add_argument("--netmask", required=True)
    args = parser.parse_args()

    hosts = arp_scan(args.iface_name, args.iface_ip, args.netmask)
    print(json.dumps(hosts))


if __name__ == "__main__":
    _main()