import asyncio
from dbus_fast.aio import MessageBus
from dbus_fast.constants import BusType

from gatt_application import Application
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'

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
        print('GattManager1 interface not found')
        return
    bluez_adapter_introspect = await bus.introspect("org.bluez", adapter)
    bluez_adapter = bus.get_proxy_object("org.bluez", adapter, bluez_adapter_introspect)
    bluez_gatt_manager = bluez_adapter.get_interface(GATT_MANAGER_IFACE)
    
    app = Application()

    await bluez_gatt_manager.call_register_application(app.get_path(), {})

asyncio.run(main())
