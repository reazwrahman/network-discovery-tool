import asyncio
from zeroconf.asyncio import AsyncZeroconf, AsyncServiceBrowser


class MyListener:
    def __init__(self, azc):
        self.azc = azc

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


async def main():
    selected_ip = "192.168.1.37"
    azc = AsyncZeroconf(interfaces=[selected_ip])
    listener = MyListener(azc)

    # Commonly used IoT service types to look for
    services_to_watch = ["_airplay._tcp.local.", "_http._tcp.local.", "_printer._tcp.local."]

    browser = AsyncServiceBrowser(azc.zeroconf, services_to_watch, listener)

    print("Listening for 10 seconds...")
    await asyncio.sleep(10)
    await azc.async_close()


if __name__ == "__main__":
    asyncio.run(main())