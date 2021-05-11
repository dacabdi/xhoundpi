'''
Format converters for message fields
'''

import re
from typing import Tuple
from decimal import localcontext, Inexact, Decimal

from .direction import CoordAxis, Direction

class NMEADataFormatter:
    '''
    Transforms values from decimal degrees to
    high precision NMEA geographic co-ordinates
    '''

    LO_PRES = 5
    HI_PRES = 7
    DEC_1 = Decimal('1')
    FORMAT = '{{degs:0{degs_width}n}}{{mins:0{mins_width}.{prec}f}}'

    def degmins_to_decdeg(self, degmins: str, direction: Direction) -> Decimal:
        '''
        Converts a geographic co-ordinate given in
        (d)ddmm.mmmmm(mm) format to signed decimal degrees
        '''
        decdeg = Decimal(self._degmins_to_decdeg(degmins))
        return decdeg.copy_negate() if direction in (Direction.S, Direction.W) else decdeg

    def decdeg_to_degmins(self, dec_deg: Decimal, axis: CoordAxis, hipres: bool = False
    ) -> Tuple[str, Direction]:
        '''
        Converts a geographic co-ordinate given in
        signed decimal degrees to (d)ddmm.mmmmm(m*) format

        NOTE there is no official documentation that states that
        the NMEA format will be fixed and always include trailing
        and leading zeros. Apparently any format is admissible,
        We will be compiling here sources that indicate which format
        each hardware source seems to use. For now, we assume all leading
        and trailing zeros are kept.

        ublox devices:
            https://portal.u-blox.com/s/question/0D52p00008HKDHLCA5/are-the-latitude-and-longitude-values-in-the-gpgga-message-fixed-format-or-variable
        '''
        template, direction, degs, mins = self._get_data(dec_deg, axis, hipres)
        return template.format(degs=degs, mins=mins), direction

    @classmethod
    def height_field_m_to_height_mm(cls, field: str) -> Decimal:
        '''
        Converts an NMEA height field in meters
        into a decimal millimetric representation
        '''
        return Decimal(field).scaleb(3)

    @classmethod
    def height_mm_to_height_field_m(cls, height: Decimal) -> str:
        '''
        Converts an NMEA height field in meters
        into a decimal millimetric representation
        '''
        return str(height.scaleb(-3))

    @classmethod
    def is_highpres(cls, value: str):
        '''
        Determines if a geographic co-ordinate given in
        (d)ddmm.mmmmm(mm) format is NMEA high precision mode
        '''
        return len(value) - value.find('.') > 7

    @classmethod
    def _get_data(cls, dec_deg: Decimal, axis: CoordAxis, hipres: bool
    ) -> Tuple[str, Direction, int, Decimal]:
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
        degs, mins = divmod(dec_deg, cls.DEC_1)
        degs = degs.copy_abs()
        mins = mins.copy_abs()
        with localcontext() as ctx:
            # NOTE
            # 1. the log10 is very unlikely to yield an exact value
            # 2. the mins * 60 operation can also be inexact, just provide enough precision
            ctx.traps[Inexact] = False
            if not degs.is_zero() and degs.log10() > deg_length:
                raise ValueError('Too many digits in decimal degrees result')
            mins *= 60
        return template, direction, int(degs), mins

    @classmethod
    #pylint: disable=invalid-name
    def _degmins_to_decdeg(cls, dm: str) -> Decimal:
        if not dm or dm == '0':
            return Decimal(0)
        d, m = re.match(r'^(\d+)(\d\d\.\d+)$', dm).groups()
        with localcontext() as ctx:
            # NOTE we cannot expect exactitude in this operation
            ctx.traps[Inexact] = False
            return Decimal(d) + Decimal(m) / Decimal(60)

class UBXDataFormatter:
    '''
    Transform values from decimal degrees to
    high precision UBX geographic co-ordinates
    '''

    # TODO store the Decimal instead of the base
    BASE_RES = 7
    HIGH_RES = 9
    DEC_1 = Decimal('1')
    DEC_0_1 = Decimal('0.1')
    MAX = 2147483647
    MIN = -2147483648

    def integer_to_decdeg(self, base: int, hires: int = 0) -> Decimal:
        '''
        Converts an UBX integer geographic
        co-ordinate into signed decimal degrees
        '''
        base_dec  = Decimal(base ).scaleb(-self.BASE_RES)
        hires_dec = Decimal(hires).scaleb(-self.HIGH_RES)
        return base_dec + hires_dec

    def integer_to_height_mm(self, base: int, hires: int = 0) -> Decimal:
        '''
        Converts signed altitude value from two integer
        components into decimal millimeters representation
        '''
        return base + (hires * self.DEC_0_1)

    def decdeg_to_integer(self, decdeg: Decimal) -> Tuple[int, int]:
        '''
        Converts signed decimal degrees
        into an UBX integer geographic co-ordinate
        '''
        base, frac = divmod(decdeg.scaleb(self.BASE_RES), self.DEC_1)
        hi_res, _ = divmod(frac.scaleb(self.HIGH_RES - self.BASE_RES), self.DEC_1)
        return int(base.to_integral_exact()), int(hi_res.to_integral_exact())

    def height_mm_to_integer(self, height_mm: Decimal) -> Tuple[int, int]:
        '''
        Converts signed altitude value from decimal millimeters
        to two integer components representation
        '''
        base, frac = divmod(height_mm, self.DEC_1)
        hi_res, _ = divmod(frac.scaleb(self.DEC_1), self.DEC_1)
        return int(base.to_integral_exact()), int(hi_res.to_integral_exact())

    def minimize_correction(self, base: int, hires: int, midpoint: int = 50) -> Tuple[int, int]:
        '''
        Comply with UBX correction minization
        '''
        if base not in [self.MAX, self.MIN] and abs(hires) >= midpoint:
            sign = self._sign(base)
            if sign != self._sign(hires):
                raise ValueError('Operation not defined for not matching signs')
            base += sign
            hires -= (midpoint * 2) * sign
        return base, hires

    @classmethod
    def _sign(cls, val: int) -> int:
        return -1 if val < 0 else 1
