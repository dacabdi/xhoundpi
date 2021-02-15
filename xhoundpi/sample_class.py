"""Sample Class"""

class SampleClass():
    """Sample Class is a temporary placeholder"""

    def __init__(self, init_value):
        self.init_value = init_value

    def get_value(self):
        """Retuns the internal value"""
        return self.init_value

    def increment_value(self):
        """Increments the internal value"""
        self.init_value += 1
