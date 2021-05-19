'''
Basic operations on Decimal type values
'''

# pylint: disable=invalid-name
# NOTE this code is based off  https://docs.python.org/3/library/decimal.html#recipes
# it will be ignored from styling and test coverage

from decimal import (
    getcontext,
    localcontext,
    Overflow,
    DivisionByZero,
    InvalidOperation,
    FloatOperation,
    Inexact,
    ROUND_HALF_EVEN,
    Decimal)
from typing import Tuple
from xhoundpi import geocoordinates

def setup_common_decimal_context(pres: int = 24):
    '''
    Sets up global context
    '''
    ctx = getcontext()
    ctx.traps[Overflow] = True
    ctx.traps[DivisionByZero] = True
    ctx.traps[InvalidOperation] = True
    ctx.traps[FloatOperation] = True
    ctx.traps[Inexact] = True
    ctx.rounding=ROUND_HALF_EVEN
    getcontext().prec = pres

def pi():
    '''Compute Pi to the current precision.

    >>> print(pi())
    3.141592653589793238462643383

    '''
    with localcontext() as ctx:
        ctx.traps[Inexact] = False
        ctx.prec += 2  # extra digits for intermediate steps
        three = Decimal(3)      # substitute "three=3.0" for regular floats
        lasts, t, s, n, na, d, da = 0, three, 3, 1, 0, 0, 24
        while s != lasts:
            lasts = s
            n, na = n+na, na+8
            d, da = d+da, da+32
            t = (t * n) / d
            s += t
        ctx.prec -= 2
        return +s               # unary plus applies the new precision

with localcontext() as c:
    c.traps[Inexact] = False
    c.prec = 64
    PI = pi()
    DEG180 = Decimal("180")
    DEG_RAD_RATIO = PI / DEG180
    MINUTE = Decimal("1") / Decimal("60")
    EQUAT_RAD_M = Decimal("6378137")
    POLAR_RAD_M = Decimal("6356752.314")
    SQRD_RADIAL_RATIO = (POLAR_RAD_M**2 / EQUAT_RAD_M**2)
    ELLIPSOID_ECC_SQRD = 1 - SQRD_RADIAL_RATIO

def geodethic_to_ecef(point: geocoordinates) -> Tuple[Decimal, Decimal, Decimal]:
    '''
    Function to convert from Geodethic coordinates
    to Earth Centered - Earth Fixed (ECEF) coordinate system
    ref: https://en.wikipedia.org/wiki/Geographic_coordinate_conversion#From_geodetic_to_ECEF_coordinates '''#pylint: disable=line-too-long

    lat = point.lat
    lon = point.lon
    alt = point.alt

    prime_vert_rad = EQUAT_RAD_M / Decimal.sqrt(1 - ELLIPSOID_ECC_SQRD * sin(deg_to_rad(lat)))

    x_coord = (prime_vert_rad + alt) * cos(deg_to_rad(lat)) * cos(deg_to_rad(lon))
    y_coord = (prime_vert_rad + alt) * cos(deg_to_rad(lat)) * sin(deg_to_rad(lon))
    z_coord = (SQRD_RADIAL_RATIO * prime_vert_rad + alt) * sin(deg_to_rad(lat))

    return x_coord, y_coord, z_coord

def exp(x):
    '''Return e raised to the power of x.  Result type matches input type.

    >>> print(exp(Decimal(1)))
    2.718281828459045235360287471
    >>> print(exp(Decimal(2)))
    7.389056098930650227230427461
    >>> print(exp(2.0))
    7.38905609893
    >>> print(exp(2+0j))
    (7.38905609893+0j)

    '''
    with localcontext() as ctx:
        ctx.traps[Inexact] = False
        ctx.prec += 2  # extra digits for intermediate steps
        i, lasts, s, fact, num = 0, 0, 1, 1, 1
        while s != lasts:
            lasts = s
            i += 1
            fact *= i
            num *= x
            s += num / fact
        ctx.prec -= 2
        return +s

def cos(x):
    '''Return the cosine of x as measured in radians.

    The Taylor series approximation works best for a small value of x.
    For larger values, first compute x = x % (2 * pi).

    >>> print(cos(Decimal('0.5')))
    0.8775825618903727161162815826
    >>> print(cos(0.5))
    0.87758256189
    >>> print(cos(0.5+0j))
    (0.87758256189+0j)

    '''
    with localcontext() as ctx:
        ctx.traps[Inexact] = False
        ctx.prec += 2  # extra digits for intermediate steps
        i, lasts, s, fact, num, sign = 0, 0, 1, 1, 1, 1
        while s != lasts:
            lasts = s
            i += 2
            fact *= i * (i-1)
            num *= x * x
            sign *= -1
            s += num / fact * sign
        ctx.prec -= 2
        return +s

def sin(x):
    '''Return the sine of x as measured in radians.

    The Taylor series approximation works best for a small value of x.
    For larger values, first compute x = x % (2 * pi).

    >>> print(sin(Decimal('0.5')))
    0.4794255386042030002732879352
    >>> print(sin(0.5))
    0.479425538604
    >>> print(sin(0.5+0j))
    (0.479425538604+0j)

    '''
    with localcontext() as ctx:
        ctx.traps[Inexact] = False
        ctx.prec += 2  # extra digits for intermediate steps
        i, lasts, s, fact, num, sign = 1, 0, x, 1, x, 1
        while s != lasts:
            lasts = s
            i += 2
            fact *= i * (i-1)
            num *= x * x
            sign *= -1
            s += num / fact * sign
        ctx.prec -= 2
        return +s

def deg_to_rad(deg: Decimal):
    '''
    Convert from degrees to radians
    '''
    return deg * DEG_RAD_RATIO
