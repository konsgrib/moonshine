from abc import ABC, abstractmethod


class SensorValue:
    def __init__(self, status_code, value, message):
        self.status_code = status_code
        self.value = value
        self.message = message

    def __repr__(self):
        return str(self.__dict__)


class Creator(ABC):

    @abstractmethod
    def factory_method(self):
        pass

    def get_data(self, *args, **kwargs):
        sensor = self.factory_method()
        result = sensor.get_value(*args, **kwargs)
        return result


class Sensor(ABC):
    @abstractmethod
    def get_value(self, *args, **kwargs) -> SensorValue:
        pass
