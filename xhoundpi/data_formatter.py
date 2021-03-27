""" Format converters for message fields """

import math
from typing import Callable, Tuple

from .direction import (CoordAxis,
                       Direction)

class NMEADataFormatter:
    """
    Transforms values from decimal degrees to
    high precision NMEA geographic co-ordinates
    """

    LO_PRES = 5
    HI_PRES = 7
    FORMAT = '{{degs:0{degs_width}n}}{{mins:0{mins_width}.{prec}f}}'

    def __init__(self, degmins_to_decdeg: Callable):
        self.__degmins_to_decdeg = degmins_to_decdeg

    def degmins_to_decdeg(self, degmins: str, direction: Direction) -> float:
        """
        Converts a geographic co-ordinate given in
        (d)ddmm.mmmmm(mm) format to signed decimal degrees

        Args:
            degmins (str): a geographic co-ordinate given in (d)ddmm.mmmmm(mm)
            direction (Direction): used to sign the decimal degress
        Returns:
            decimal degrees (float)
        """
        decdeg = self.__degmins_to_decdeg(degmins)
        return -decdeg if direction in (Direction.S, Direction.W) else decdeg

    def decdeg_to_degmins(self, dec_deg: float, axis: CoordAxis, hipres: bool = False
    ) -> Tuple[str, Direction]:
        """
        Converts a geographic co-ordinate given in
        signed decimal degrees to (d)ddmm.mmmmm(m*) format
        """
        template, direction, degs, mins = self._get_data(dec_deg, axis, hipres)
        return template.format(degs=degs, mins=mins), direction

    @classmethod
    def _get_data(cls, dec_deg: float, axis: CoordAxis, hipres: bool
    ) -> Tuple[str, Direction]:
        if axis is CoordAxis.LON:
            direction = Direction.E if dec_deg >= 0 else Direction.W
            deg_length = 3
        else: # axis is CoordAxis.LAT
            direction = Direction.N if dec_deg >= 0 else Direction.S
            deg_length = 2
        precision = cls.HI_PRES if hipres else cls.LO_PRES
        template = cls.FORMAT.format(
            degs_width=deg_length,
            mins_width=3 + precision,
            prec=precision)
        mins, degs = math.modf(abs(dec_deg))
        if degs != 0. and math.log10(degs) > deg_length:
            raise ValueError('Too many digits in decimal degrees result')
        return template, direction, int(degs), mins * 60

    @classmethod
    def is_highpres(cls, value: str):
        """
        Determines if a geographic co-ordinate given in
        (d)ddmm.mmmmm(mm) format is NMEA high precision mode
        """
        return len(value) - value.find('.') == 7

class UBXDataFormatter:
    """
    Transform values from decimal degrees to
    high precision UBX geographic co-ordinates
    """

    BASE_RES = 7
    HIGH_RES = 9

    def integer_to_decdeg(self, base: int, hires: int = 0) -> float:
        """
        Converts an UBX integer geographic
        co-ordinate into signed decimal degrees
        """
        return base * 10 ** -self.BASE_RES + hires * 10 ** -self.HIGH_RES

    def decdeg_to_integer(self, decdeg: float) -> Tuple[int, int]:
        """
        Converts signed decimal degrees
        into an UBX integer geographic co-ordinate
        """
        value = decdeg * 10 ** self.BASE_RES
        frac, base = math.modf(value)
        hi_res = frac * 10 ** (self.HIGH_RES - self.BASE_RES)
        return int(base), int(hi_res)
