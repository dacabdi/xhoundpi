""" Operation status representation module """

from typing import Dict

class Status:
    """ Operation status representation """

    def __init__(self, error: Exception, metadata: Dict = None):
        self.__error = error
        self.__metadata = metadata if metadata is not None else dict()

    @classmethod
    def OK(cls, metadata: Dict = None): # pylint: disable=invalid-name
        """ Create an OK status """
        return Status(None, metadata)

    @property
    def error(self):
        """ Return internal exception if any """
        return self.__error

    @property
    def metadata(self):
        """ Return status metadata """
        return self.__metadata

    @property
    def ok(self): # pylint: disable=invalid-name
        """ Signals whether the status is succesful """
        return self.error is None

    def __eq__(self, o: object) -> bool:
        return self.__error == o.error and self.__metadata == o.metadata
