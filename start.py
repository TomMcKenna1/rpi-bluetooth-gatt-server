import asyncio
from dbus_fast import BusType, PropertyAccess
from dbus_fast.aio import MessageBus
from dbus_fast.service import ServiceInterface, method, dbus_property


class MarketMonitorApplication(ServiceInterface):
    def __init__(self):
        self.services = []
        super().__init__("marketmonitorapp")

    def add_service(self, service):
        self.services.append(service)

    @method()
    def GetManagedObjects(self) -> "a{oa{sa{sv}}}":
        response = {}

        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_chars()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()

        return response


class MarketMonitorService(ServiceInterface):
    def __init__(self, uuid, path):
        self.path = path
        self.name = "marketmonitorservice"
        self.uuid = uuid
        self.primary = True
        self.chars = []
        self.includes = []
        super().__init__(self.name)

    def get_path(self):
        return self.path

    def get_properties(self):
        return {
            "org.bluez.GattService1": {
                "UUID": self.uuid,
                "Primary": self.primary,
                "Characteristics": self.includes,
            }
        }

    def get_chars(self):
        return self.chars

    def add_char(self, char):
        self.chars.append(char)
        self.includes.append(char.get_path())

    @dbus_property(PropertyAccess.READ)
    def UUID(self) -> "s":
        return self.uuid

    @dbus_property(PropertyAccess.READ)
    def Primary(self) -> "b":
        return self.primary

    @dbus_property()
    def Includes(self) -> "ao":
        return self.includes

    @Includes.setter
    def Includes(self, value: "ao"):
        self.includes = value


class MarketMonitorChar(ServiceInterface):
    def __init__(self, path, uuid):
        self.name = "marketmonitorchar"
        self.path = path
        self.service = "/".join(path.split("/")[0:-1])
        self.uuid = uuid
        self.flags = ["read", "write"]
        self.value = 1
        super().__init__(self.name)

    def get_path(self):
        return self.path

    def get_properties(self):
        return {
            "org.bluez.GattCharacteristic1": {
                "Service": self.service,
                "UUID": self.uuid,
                "Flags": self.flags,
            }
        }

    @method()
    def ReadValue(self, opt: "a{sv}"):
        print("Read!")
        return self.value

    @method()
    def WriteValue(self, val: "ay", opt: "a{sv}"):
        self.value = val
        print("Written!")

    @method()
    def StartNotify(self):
        pass

    @method()
    def StopNotify(self):
        pass

    @dbus_property(PropertyAccess.READ)
    def UUID(self) -> "s":
        return self.uuid

    @dbus_property(PropertyAccess.READ)
    def Service(self) -> "s":
        return self.service

    @dbus_property(PropertyAccess.READ)
    def Flags(self) -> "as":
        return self.flags

    @dbus_property(PropertyAccess.READ)
    def MTU(self) -> "q":
        return 10000


class MarketMonitorAdvert(ServiceInterface):
    def __init__(self):
        self.name = "marketmonitor"
        self.device_name = self.name
        self.local_name = self.name
        self.type = "peripheral"
        self.service_uuids = []
        self.manufacturer_data = {}
        self.solicit_uuids = []
        self.service_data = {}
        self.data = {}
        self.discoverable = True
        self.discoverable_timeout = 0
        self.includes = []
        super().__init__(self.name)

    @method()
    def Release(self):
        print("Released service")

    @dbus_property(PropertyAccess.READ)
    def Type(self) -> "s":
        return self.type

    @dbus_property()
    def ServiceUUIDs(self) -> "as":
        return self.service_uuids

    @ServiceUUIDs.setter
    def ServiceUUIDs(self, value: "as"):
        self.service_uuids = value

    @dbus_property()
    def ManufacturerData(self) -> "a{sv}":
        return self.manufacturer_data

    @ManufacturerData.setter
    def ManufacturerData(self, value: "a{sv}"):
        self.manufacturer_data = value

    @dbus_property()
    def SolicitUUIDs(self) -> "as":
        return self.solicit_uuids

    @SolicitUUIDs.setter
    def SolicitUUIDs(self, value: "as"):
        self.solicit_uuids = value

    @dbus_property()
    def ServiceData(self) -> "a{sv}":
        return self.service_data

    @ServiceData.setter
    def ServiceData(self, value: "a{sv}"):
        self.service_data = value

    @dbus_property()
    def Data(self) -> "a{sv}":
        return self.data

    @Data.setter
    def Data(self, value: "a{sv}"):
        self.data = value

    @dbus_property()
    def Discoverable(self) -> "b":
        return self.discoverable

    @Discoverable.setter
    def Discoverable(self, value: "b"):
        self.discoverable = value

    @dbus_property()
    def DiscoverableTimeout(self) -> "q":
        return self.discoverable_timeout

    @DiscoverableTimeout.setter
    def DiscoverableTimeout(self, value: "q"):
        self.discoverable_timeout = value

    @dbus_property()
    def Includes(self) -> "as":
        return self.includes

    @Includes.setter
    def Includes(self, value: "as"):
        self.includes = value

    @dbus_property()
    def LocalName(self) -> "s":
        return self.local_name

    @LocalName.setter
    def LocalName(self, value: "s"):
        self.local_name = value

    @dbus_property()
    def DeviceName(self) -> "s":
        return self.device_name

    @DeviceName.setter
    def DeviceName(self, value: "s"):
        self.device_name = value


async def main():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    advert = MarketMonitorAdvert()
    bus.export("/org/bluez/example/advertisement", advert)
    print("added advert")
    application = MarketMonitorApplication()
    bus.export("/", application)
    print("added app")
    service = MarketMonitorService("0xFFFF", "/org/bluez/example/service")
    bus.export("/org/bluez/example/service", service)
    print("added service")
    char = MarketMonitorChar("0x1234", "/org/bluez/example/service/char1")
    bus.export("/org/bluez/example/service/char1", char)
    print("added characteristic")
    service.add_char(char)
    application.add_service(service)
    print("introspecting...")
    intro = await bus.introspect("org.bluez", "/org/bluez/hci0")
    print("done")
    # print([[method.name for method in interface.methods] for interface in intro.interfaces])
    obj = bus.get_proxy_object("org.bluez", "/org/bluez/hci0", intro)
    adv_man_proxy = obj.get_interface("org.bluez.LEAdvertisingManager1")
    adapter_proxy = obj.get_interface("org.bluez.Adapter1")
    gatt_manager = obj.get_interface("org.bluez.GattManager1")
    await adapter_proxy.set_powered(True)
    await adapter_proxy.set_discoverable(True)
    await adapter_proxy.set_pairable(True)
    before = await adv_man_proxy.get_active_instances()
    print(before)
    try:
        appreg = await gatt_manager.call_register_application("/", {})
    except Exception as e:
        print(e)
        exit()
    awd = await adv_man_proxy.call_register_advertisement(
        "/org/bluez/example/advertisement", {}
    )
    after = await adv_man_proxy.get_active_instances()
    print(after)


asyncio.run(main())
while True:
    asyncio.sleep(1)
