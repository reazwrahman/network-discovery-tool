import ipaddress
import ipaddress
import asyncio


def get_subnet_ips(ip, netmask):
    network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
    return [str(host) for host in network.hosts()]


async def async_ping(ip):
    proc = await asyncio.create_subprocess_exec(
        "ping", "-c", "1", "-W", "1", ip,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    await proc.communicate()
    if proc.returncode == 0:
        print(f'[Active]: {ip}')
        return ip
    else:
        return None


async def ping_sweep_async(ip, netmask):
    tasks = [async_ping(ip) for ip in get_subnet_ips(ip, netmask)]
    results = await asyncio.gather(*tasks)
    return [host for host in results if host]


def run_ping_sweep(ip, netmask):
    return asyncio.run(ping_sweep_async(ip, netmask))


def _main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Perform a ping sweep for a given IP/netmask.")
    parser.add_argument("--ip", required=True)
    parser.add_argument("--netmask", required=True)
    args = parser.parse_args()

    hosts = run_ping_sweep(args.ip, args.netmask)
    print(json.dumps(hosts))


if __name__ == "__main__":
    _main()