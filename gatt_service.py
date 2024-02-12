from dbus_fast.service import ServiceInterface, method


class Service(ServiceInterface):
    """
    org.bluez.GattService1 interface implementation
    """

    PATH_BASE = "/org/bluez/example/service"

    def __init__(self, index, uuid, primary):
        self.path = self.PATH_BASE + str(index)

        # framework requires hex string so auto format it if an int was specified
        if isinstance(uuid, int):
            uuid = "0x%x" % uuid

        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        ServiceInterface.__init__(self, 'org.bluez.GattService1')
        ServiceInterface.__init__(self, 'org.freedesktop.DBus.Properties')

    def get_properties(self):
        return {
            "org.bluez.GattService1": {
                "UUID": self.uuid,
                "Primary": self.primary,
                "Characteristics": self.get_characteristic_paths(),
            }
        }

    def get_path(self):
        return self.path

    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)

    def get_characteristic_paths(self):
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result

    def get_characteristics(self):
        return self.characteristics

    @method()
    def GetAll(self, interface: 's') -> 'a{sv}':
        if interface != 'org.bluez.GattService1':
            raise Exception("Invalid interface name")

        return self.get_properties()['org.bluez.GattService1']
