from .sensor import Creator, Sensor


class MaxCreator(Creator):
    def factory_method(self):
        return MaxSensor()


class MaxSensor(Sensor):
    def get_value(self, *args, **kwargs):
        return "{result of Max sensor}"
