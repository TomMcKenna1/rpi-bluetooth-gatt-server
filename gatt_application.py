from dbus_fast.service import ServiceInterface, method


class Application(ServiceInterface):
    """
    org.bluez.GattApplication1 interface implementation
    """

    def __init__(self):
        self.path = "/"
        self.services = []
        ServiceInterface.__init__(self, 'org.freedesktop.DBus.ObjectManager')

    def get_path(self):
        return self.path

    def add_service(self, service):
        self.services.append(service)

    @method()
    def GetManagedObjects(self) -> "a{oa{sa{sv}}}":
        response = {}
        print("GetManagedObjects")

        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                descs = chrc.get_descriptors()
                for desc in descs:
                    response[desc.get_path()] = desc.get_properties()

        return response
