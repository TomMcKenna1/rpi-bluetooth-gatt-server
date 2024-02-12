import asyncio
from dbus_fast.service import method
from dbus_fast.aio import MessageBus
from dbus_fast.constants import BusType

from gatt_application import Application
from gatt_service import Service
from gatt_characteristic import Characteristic
from gatt_descriptor import Descriptor

DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
GATT_MANAGER_IFACE = "org.bluez.GattManager1"


class HeartRateService(Service):
    """
    Fake Heart Rate Service that simulates a fake heart beat and control point
    behavior.

    """

    HR_UUID = "0000180d-0000-1000-8000-00805f9b34fb"

    def __init__(self, index):
        Service.__init__(self, index, self.HR_UUID, True)
        self.energy_expended = 0


class TestCharacteristic(Characteristic):
    """
    Dummy test characteristic. Allows writing arbitrary bytes to its value, and
    contains "extended properties", as well as a test descriptor.

    """

    TEST_CHRC_UUID = "12345678-1234-5678-1234-56789abcdef1"

    def __init__(self, index, service):
        Characteristic.__init__(
            self,
            index,
            self.TEST_CHRC_UUID,
            ["read", "write"],
            service,
        )
        self.value = []

    @method()
    def ReadValue(self, options: "a{sv}") -> "ay":
        print("TestCharacteristic Read: " + repr(self.value))
        return self.value

    @method()
    def WriteValue(self, value: "ay", options: "a{sv}"):
        print("TestCharacteristic Write: " + repr(value))
        self.value = value


class TestDescriptor(Descriptor):
    """
    Dummy test descriptor. Returns a static value.

    """

    TEST_DESC_UUID = "12345678-1234-5678-1234-56789abcdef2"

    def __init__(self, index, characteristic):
        Descriptor.__init__(
            self, index, self.TEST_DESC_UUID, ["read", "write"], characteristic
        )

    @method()
    def ReadValue(self, options: 'a{sv}') -> 'ay':
        return bytearray("test", "utf-8")


async def find_adapter(bus):
    bluez_introspect = await bus.introspect("org.bluez", "/")
    bluez_proxy_object = bus.get_proxy_object("org.bluez", "/", bluez_introspect)
    bluez_object_manager = bluez_proxy_object.get_interface(DBUS_OM_IFACE)
    objects = await bluez_object_manager.call_get_managed_objects()
    for o, props in objects.items():
        if GATT_MANAGER_IFACE in props:
            return o
    return None


async def main():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    adapter = await find_adapter(bus)
    if not adapter:
        print("GattManager1 interface not found")
        return
    bluez_adapter_introspect = await bus.introspect("org.bluez", adapter)
    bluez_adapter = bus.get_proxy_object("org.bluez", adapter, bluez_adapter_introspect)
    bluez_gatt_manager = bluez_adapter.get_interface(GATT_MANAGER_IFACE)

    app = Application()
    service = HeartRateService(0)
    characteristic = TestCharacteristic(0, service)
    descriptor = TestDescriptor(0, characteristic)
    bus.export(descriptor.get_path(), descriptor)
    characteristic.add_descriptor(descriptor)
    bus.export(characteristic.get_path(), characteristic)
    service.add_characteristic(characteristic)
    bus.export(service.get_path(), service)
    app.add_service(service)
    bus.export("/", app)

    await bluez_gatt_manager.call_register_application(app.get_path(), {})


asyncio.run(main())
