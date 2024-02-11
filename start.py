import asyncio
from dbus_fast import BusType
from dbus_fast.aio import MessageBus
from dbus_fast.service import ServiceInterface, method, dbus_property


class MarketMirrorAdvert(ServiceInterface):
    def __init__(self):
        self.name = "Market Monitor"
        self.type = "peripheral"
        super().__init__(self.name)

    @method
    def Release(self):
        print("Released service")

    @dbus_property
    def Type(self) -> "s":
        return self.type

    @dbus_property
    def ServiceUUIDs(self) -> "as":
        pass

    @dbus_property
    def ManufacturerData(self) -> "a{sv}":
        pass

    @dbus_property
    def SolicitUUIDs(self) -> "as":
        pass

    @dbus_property
    def ServiceData(self) -> "a{sv}":
        pass

    @dbus_property
    def Data(self) -> "a{sv}":
        pass

    @dbus_property
    def Discoverable(self) -> "b":
        return True


async def main():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    intro = await bus.introspect("org.bluez", "/org/bluez/hci0")
    # print([[method.name for method in interface.methods] for interface in intro.interfaces])
    obj = bus.get_proxy_object("org.bluez", "/org/bluez/hci0", intro)
    adapter_proxy = obj.get_interface("org.bluez.Adapter1")
    awd = await adapter_proxy.call_get_discovery_filters()
    print(awd)


asyncio.run(main())
