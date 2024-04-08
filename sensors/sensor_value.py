class SensorValue:
    def __init__(self, status_code, value, message):
        self.status_code = status_code
        self.value = value
        self.message = message

    def __repr__(self):
        return str(self.__dict__)
