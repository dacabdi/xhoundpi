""" Frame geometry """

from typing import Tuple, Union

class Geometry:
    """
    Models frame geometry in pixels
    """

    def __init__(self, rows: int, cols: int, channels: int=3, depth: int=8):
        self.__rows = rows
        self.__cols = cols
        self.__channels = channels
        self.__depth = depth

    @property
    def row_major(self) -> Tuple[int, int]:
        """
        Return tuple ordering by rows
        """
        return self.rows, self.cols

    @property
    def col_major(self) -> Tuple[int, int]:
        """
        Return tuple ordering by columns
        """
        return self.cols, self.rows

    @property
    def rows(self)-> int:
        """
        Pixel rows
        """
        return self.__rows

    @property
    def cols(self) -> int:
        """
        Pixel columns
        """
        return self.__cols

    @property
    def channels(self) -> int:
        """
        Number of channels
        """
        return self.__channels

    @property
    def depth(self) -> int:
        """
        Channel depth (in bits)
        """
        return self.__depth

    def shape(self, use_col_major: bool=False
    ) -> Union[Tuple[int, int], Tuple[int, int, int]]:
        """
        Generate shape with channels
        """
        base = (self.col_major
            if use_col_major
            else self.row_major)
        if self.channels > 1:
            return base + (self.channels,)
        return base

    def __eq__(self, other) -> bool:
        return (self.rows == other.rows
            and self.cols == other.cols
            and self.channels == other.channels
            and self.depth == other.depth)
