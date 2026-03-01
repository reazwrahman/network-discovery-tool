import asyncio


COMMON_PORTS = [80, 443, 554, 8000, 8080, 8554, 5353, 9090]

async def scan_port(ip, port, timeout=1):
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port),
            timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return port  # open
    except:
        return None  # closed or filtered

async def scan_host_ports(ip):
    tasks = [scan_port(ip, p) for p in COMMON_PORTS]
    results = await asyncio.gather(*tasks)
    results = [p for p in results if p]
    print(f'{ip}: {results}')
    return {ip: [p for p in results if p]}

async def scan_all_hosts(hosts):
    tasks = [scan_host_ports(ip) for ip in hosts]
    results = await asyncio.gather(*tasks)
    return results


def run_port_scan(hosts):
    """Scan a list of hosts for common open ports."""
    return asyncio.run(scan_all_hosts(hosts))


if __name__ == "__main__":
    hosts = ['192.168.1.1', '192.168.1.12', '192.168.1.37', '192.168.1.174', '192.168.1.184', '192.168.1.198', '192.168.1.209', '192.168.1.221', '192.168.1.232', '192.168.1.241']
    results = run_port_scan(hosts)
    print(results)