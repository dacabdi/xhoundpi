""" Operation status representation module """

from __future__ import annotations
from typing import Dict, Union

class Status:
    """ Operation status representation """

    def __init__(self, error: Union[Exception, None], metadata: Dict = None):
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

    def __eq__(self, o: Status) -> bool:
        return (
            type(self.error) is type(o.error)
            and ((self.error is None and o.error is None)
                 or self.error.args == o.error.args)
            and self.metadata == o.metadata
        )

    def __str__(self):
        return f'ok={self.ok}, error={repr(self.error)}, metadata={self.metadata}'

    def __repr__(self) -> str:
        return '<%s.%s(%s) object at %s>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            str(self),
            hex(id(self)))
