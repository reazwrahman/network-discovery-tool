import asyncio

from zeroconf import BadTypeInNameException
from zeroconf.asyncio import AsyncZeroconf, AsyncServiceBrowser, ServiceListener


class MyListener(ServiceListener):
    def __init__(self, azc, services = [], should_resolve_details = False):
        self.azc = azc
        self.discovered_services = services
        self.should_resolve_details:bool = should_resolve_details

    def add_service(self, zc, type_, name):
        print(type_, name)
        self.discovered_services.append(name)
        if self.should_resolve_details:
            asyncio.create_task(self.resolve_details(type_, name))

    def remove_service(self, zc, type_, name):
        pass

    def update_service(self, zc, type_, name):
        pass

    async def resolve_details(self, type_, name):
        # This is where the magic happens
        try:
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

        except BadTypeInNameException:
            # We ignore this because it just means a 'Category' was mistaken for a 'Device'
            pass
        except Exception as e:
            # Catch other random network glitches (timeouts, etc.)
            print(f"Skipping {name}: {e}")


async def run_mdns_discovery(interface_ip, duration_sec=10):
    """Run mDNS discovery on the given interface IP for specified duration.
    Returns a list of discovered services."""

    async def discover(azc:AsyncZeroconf, listener: MyListener):
        AsyncServiceBrowser(azc.zeroconf, listener.discovered_services, listener)
        print(f"Listening for {duration_sec} seconds on {interface_ip}...")
        await asyncio.sleep(duration_sec)
        await azc.async_close()

    ## watch for all service types first
    print(" ------ Phase 1: Running a wide cast net to find all the service names in the UDP ------")
    azc = AsyncZeroconf(interfaces=[interface_ip])
    listener = MyListener(azc, ["_services._dns-sd._udp.local."], False)
    await discover(azc, listener)

    ## now run a more targeted discovery for device details
    print(" ------ Phase 2: Now running a targeted discovery with the devices found in phase 1 ------")
    azc = AsyncZeroconf(interfaces=[interface_ip])
    targeted_listener = MyListener(azc, listener.discovered_services, True)
    await discover(azc, targeted_listener)

    return listener.discovered_services


async def main():
    selected_ip = "192.168.1.37"
    await run_mdns_discovery(selected_ip, duration_sec=10)


if __name__ == "__main__":
    asyncio.run(main())