""" Extensions/utilities for class manipulation """

# modded from: https://mgarod.medium.com/dynamically-add-a-method-to-a-class-in-python-c49204b85bd6
def add_method(cls):
    """ Extend a class by adding a method during runtime """
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func
    return decorator
