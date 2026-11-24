import asyncio


# COMMON_PORTS = [80, 443, 554, 8000, 8080, 8554, 5353, 9090, 21, 23, 5050]


COMMON_PORTS = [
    {"port": 20, "protocol": "FTP Data", "description": "File Transfer Protocol (Data)"},
    {"port": 21, "protocol": "FTP Control", "description": "File Transfer Protocol (Control)"},
    {"port": 22, "protocol": "SSH / SFTP", "description": "Secure Shell and encrypted file transfer"},
    {"port": 23, "protocol": "Telnet", "description": "Unencrypted remote terminal access"},
    {"port": 25, "protocol": "SMTP", "description": "Simple Mail Transfer Protocol (outgoing mail routing)"},
    {"port": 53, "protocol": "DNS", "description": "Domain Name System lookups"},
    {"port": 67, "protocol": "DHCP Server", "description": "Dynamic Host Configuration Protocol"},
    {"port": 68, "protocol": "DHCP Client", "description": "Dynamic Host Configuration Protocol"},
    {"port": 80, "protocol": "HTTP", "description": "Standard unencrypted web traffic"},
    {"port": 110, "protocol": "POP3", "description": "Post Office Protocol v3 (email retrieval)"},
    {"port": 123, "protocol": "NTP", "description": "Network Time Protocol (clock synchronization)"},
    {"port": 143, "protocol": "IMAP", "description": "Internet Message Access Protocol (email sync)"},
    {"port": 161, "protocol": "SNMP", "description": "Simple Network Management Protocol"},
    {"port": 162, "protocol": "SNMP Trap", "description": "SNMP asynchronous notifications"},
    {"port": 443, "protocol": "HTTPS", "description": "Encrypted web traffic over TLS/SSL"},
    {"port": 445, "protocol": "SMB", "description": "Server Message Block (Windows file sharing)"},
    {"port": 587, "protocol": "SMTP Submission", "description": "Authenticated outgoing email submission"},
    {"port": 993, "protocol": "IMAPS", "description": "Encrypted IMAP over TLS/SSL"},
    {"port": 995, "protocol": "POP3S", "description": "Encrypted POP3 over TLS/SSL"},
    {"port": 1433, "protocol": "MS SQL", "description": "Microsoft SQL Server database"},
    {"port": 3306, "protocol": "MySQL", "description": "MySQL and MariaDB database"},
    {"port": 3389, "protocol": "RDP", "description": "Microsoft Remote Desktop Protocol"},
    {"port": 5432, "protocol": "PostgreSQL", "description": "PostgreSQL database"},
    {"port": 8080, "protocol": "HTTP Alternate", "description": "Web proxies and local development servers"},
    {"port": 5050, "protocol": "custom", "description": "custom port for local applications"},
]
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
    tasks = [scan_port(ip, p["port"]) for p in COMMON_PORTS]
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
