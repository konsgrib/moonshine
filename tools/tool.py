import RPi.GPIO as GPIO
from abc import ABC, abstractmethod


class ToolValue:
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

    def update_state(self, *args, **kwargs):
        tool = self.factory_method()
        self.state = tool.set_state(*args, **kwargs)
        return self.state

    def get_state(self):
        tool = self.factory_method()
        return tool.get_state()


class Tool(ABC):
    @abstractmethod
    def set_state(self, *args, **kwargs):
        pass

    def get_state(self):
        pass


class RelayCreator(Creator):
    def __init__(self, pin):
        self.pin = pin

    def factory_method(self):
        return RelayTool(self.pin)


class RelayTool(Tool):
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

    def set_state(self, state):
        try:
            if state != self._get_state():
                GPIO.output(self.pin, state)
                return ToolValue(200, state, "OK")
            return ToolValue(200, state, "OK")
        except KeyboardInterrupt:
            return ToolValue(200, state, "Extit pressed Ctrl+C")
        except Exception as e:
            return ToolValue(500, state, str(e))

    def _get_state(self):
        return GPIO.input(self.pin)

    def get_state(self):
        return GPIO.input(self.pin)
