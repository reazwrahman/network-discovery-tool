import asyncio
from zeroconf.asyncio import AsyncZeroconf, AsyncServiceBrowser, ServiceListener


class MyListener(ServiceListener):
    def __init__(self, azc):
        self.azc = azc
        self.discovered_services = []

    def add_service(self, zc, type_, name):
        # We found an instance! Now we create a task to get its details.
        asyncio.ensure_future(self.resolve_details(type_, name))

    def remove_service(self, zc, type_, name):
        pass

    def update_service(self, zc, type_, name):
        pass

    async def resolve_details(self, type_, name):
        # This is where the magic happens
        info = await self.azc.async_get_service_info(type_, name)
        if info:
            print(f"\n--- Found Device: {name} ---")
            print(f"  Service Type: {type_}")
            print(f"  IP Address: {info.parsed_addresses()}")
            print(f"  Port: {info.port}")
            # TXT Records are properties/metadata
            print(f"  Metadata (TXT): {info.properties}")
            
            # Convert metadata bytes to strings for JSON serialization
            metadata = {}
            if info.properties:
                for k, v in info.properties.items():
                    key = k.decode() if isinstance(k, bytes) else k
                    val = v.decode() if isinstance(v, bytes) else v
                    metadata[key] = val
            
            # Collect for returning
            self.discovered_services.append({
                "name": name,
                "service_type": type_,
                "ip_addresses": [str(ip) for ip in info.parsed_addresses()],
                "port": info.port,
                "metadata": metadata
            })


async def run_mdns_discovery(interface_ip, duration_sec=10):
    """Run mDNS discovery on the given interface IP for specified duration.
    Returns a list of discovered services."""
    azc = AsyncZeroconf(interfaces=[interface_ip])
    listener = MyListener(azc)

    # Commonly used IoT service types to look for
    services_to_watch = ["_airplay._tcp.local.", "_http._tcp.local.", "_printer._tcp.local."]

    browser = AsyncServiceBrowser(azc.zeroconf, services_to_watch, listener)

    print(f"Listening for {duration_sec} seconds on {interface_ip}...")
    await asyncio.sleep(duration_sec)
    await azc.async_close()
    
    return listener.discovered_services


async def main():
    selected_ip = "192.168.1.37"
    await run_mdns_discovery(selected_ip, duration_sec=10)


if __name__ == "__main__":
    asyncio.run(main())