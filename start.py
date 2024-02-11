import asyncio
from dbus_fast import BusType, PropertyAccess
from dbus_fast.aio import MessageBus
from dbus_fast.service import ServiceInterface, method, dbus_property

class MarketMirrorAdvert(ServiceInterface):
    def __init__(self):
        self.name = "Market Monitor"
        self.device_name = self.name
        self.local_name = self.name
        self.type = "peripheral"
        self.service_uuids = []
        self.manufacturer_data = {}
        self.solicit_uuids = []
        self.service_data = {}
        self.data = {}
        self.discoverable = True
        self.discoverable_timeout = 100
        self.includes = []
        super().__init__(self.name)
        
    @method()
    def Release(self):
        print("Released service")
    @dbus_property(PropertyAccess.READ)
    def Type(self) -> 's':
        return self.type
    @dbus_property()
    def ServiceUUIDs(self) -> 'as':
        return self.service_uuids
    @ServiceUUIDs.setter
    def ServiceUUIDs(self, value: 'as'):
        self.service_uuids = value
    @dbus_property()
    def ManufacturerData(self) -> 'a{sv}':
        return self.manufacturer_data
    @ManufacturerData.setter
    def ManufacturerData(self, value: 'a{sv}'):
        self.manufacturer_data = value
    @dbus_property()
    def SolicitUUIDs(self) -> 'as':
        return self.solicit_uuids
    @SolicitUUIDs.setter
    def SolicitUUIDs(self, value: 'as'):
        self.solicit_uuids = value
    @dbus_property()
    def ServiceData(self) -> 'a{sv}':
        return self.service_data
    @ServiceData.setter
    def ServiceData(self, value: 'a{sv}'):
        self.service_data = value
    @dbus_property()
    def Data(self) -> 'a{sv}':
        return self.data
    @Data.setter
    def Data(self, value: 'a{sv}'):
        self.data = value
    @dbus_property()
    def Discoverable(self) -> 'b':
        return self.discoverable
    @Discoverable.setter
    def Discoverable(self, value: 'b'):
        self.discoverable = value
    @dbus_property()
    def DiscoverableTimeout(self) -> 'q':
        return self.discoverable_timeout
    @DiscoverableTimeout.setter
    def DiscoverableTimeout(self, value: 'q'):
        self.discoverable_timeout = value
    @dbus_property()
    def Includes(self) -> 'as':
        return self.includes
    @Includes.setter
    def Includes(self, value: 'as'):
        self.includes = value
    @dbus_property()
    def LocalName(self) -> 's':
        return self.local_name
    @LocalName.setter
    def LocalName(self, value: 's'):
        self.local_name = value
    @dbus_property()
    def DeviceName(self) -> 's':
        return self.device_name
    @DeviceName.setter
    def DeviceName(self, value: 's'):
        self.device_name = value


async def main():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    advert = MarketMirrorAdvert()
    bus.export('/org/bluez/example/advertisement', advert)
    intro = await bus.introspect("org.bluez", "/org/bluez/hci0")
    # print([[method.name for method in interface.methods] for interface in intro.interfaces])
    obj = bus.get_proxy_object("org.bluez", "/org/bluez/hci0", intro)
    adv_man_proxy = obj.get_interface("org.bluez.LEAdvertisingManager1")
    adapter_proxy = obj.get_interface("org.bluez.Adapter1")
    await adapter_proxy.set_powered(True)
    await adapter_proxy.set_discoverable(True)
    await adapter_proxy.set_pairable(True)
    before = await adv_man_proxy.get_active_instances()
    print(before)
    awd = await adv_man_proxy.call_register_advertisement('/org/bluez/example/advertisement', {})
    after = await adv_man_proxy.get_active_instances()
    print(after)
    


asyncio.run(main())