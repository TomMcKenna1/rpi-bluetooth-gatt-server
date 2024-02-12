from dbus_fast.service import ServiceInterface, method, signal


class Characteristic(ServiceInterface):
    """
    org.bluez.GattCharacteristic1 interface implementation
    """

    def __init__(self, index, uuid, flags, service):
        self.path = service.path + "/char" + str(index)

        # framework requires hex string so auto format it if an int was specified
        if isinstance(uuid, int):
            uuid = "0x%x" % uuid

        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.descriptors = []
        ServiceInterface.__init__(self, 'org.bluez.GattCharacteristic1')

    def get_properties(self):
        return {
            "org.bluez.GattCharacteristic1": {
                "Service": self.service.get_path(),
                "UUID": self.uuid,
                "Flags": self.flags,
                "Descriptors": self.get_descriptor_paths(),
            }
        }

    def get_path(self):
        return self.path

    def add_descriptor(self, descriptor):
        self.descriptors.append(descriptor)

    def get_descriptor_paths(self):
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    def get_descriptors(self):
        return self.descriptors

    @method('DBus.Properties')
    def GetAll(self, interface: "s") -> "a{sv}":
        if interface != "org.bluez.GattCharacteristic1":
            raise Exception("Invalid interface")

        return self.get_properties()["org.bluez.GattCharacteristic1"]

    @method()
    def ReadValue(self, options: "a{sv}") -> "ay":
        print("Default ReadValue called, returning error")
        raise Exception("Not supported")

    @method()
    def WriteValue(self, value: "ay", options: "a{sv}"):
        print("Default WriteValue called, returning error")
        raise Exception("Not supported")

    @method()
    def StartNotify(self):
        print("Default StartNotify called, returning error")
        raise Exception("Not supported")

    @method()
    def StopNotify(self):
        print("Default StopNotify called, returning error")
        raise Exception("Not supported")

    @signal('DBus.Properties')
    def PropertiesChanged(self, interface, changed, invalidated) -> "s":
        pass
