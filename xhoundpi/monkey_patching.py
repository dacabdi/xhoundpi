""" Extensions/utilities for class manipulation """

from functools import wraps

# from: https://mgarod.medium.com/dynamically-add-a-method-to-a-class-in-python-c49204b85bd6
def add_method(cls):
    """ Extend a class by adding a method during runtime """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        setattr(cls, func.__name__, wrapper)
        return func
    return decorator
