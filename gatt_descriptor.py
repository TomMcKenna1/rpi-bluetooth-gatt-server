from dbus_fast.service import ServiceInterface, method


class Descriptor(ServiceInterface):
    """
    org.bluez.GattDescriptor1 interface implementation
    """

    def __init__(self, index, uuid, flags, characteristic):
        self.path = characteristic.path + "/desc" + str(index)
        self.uuid = uuid
        self.flags = flags
        self.chrc = characteristic
        ServiceInterface.__init__(self, self.path)

    def get_properties(self):
        return {
            "org.bluez.GattDescriptor1": {
                "Characteristic": self.chrc.get_path(),
                "UUID": self.uuid,
                "Flags": self.flags,
            }
        }

    def get_path(self):
        return self.path

    @method()
    def GetAll(self, interface: "s") -> "a{sv}":
        if interface != "org.bluez.GattDescriptor1":
            raise Exception("Invalid interface")

        return self.get_properties()["org.bluez.GattDescriptor1"]

    @method()
    def ReadValue(self, options: "a{sv}") -> "ay":
        print("Default ReadValue called, returning error")
        raise Exception("Unsupported")

    @method()
    def WriteValue(self, value: "ay", options: "a{sv}"):
        print("Default WriteValue called, returning error")
        raise Exception("Unsupported")
