'''
Basic operations on Decimal type values
'''

# pylint: disable=invalid-name
# NOTE this code is based off  https://docs.python.org/3/library/decimal.html#recipes
# it will be ignored from styling and test coverage

from typing import Tuple
from collections import defaultdict
from decimal import (
    DefaultContext,
    ROUND_DOWN,
    getcontext,
    localcontext,
    Overflow,
    DivisionByZero,
    InvalidOperation,
    FloatOperation,
    Inexact,
    ROUND_HALF_EVEN,
    Decimal as D,
    DecimalTuple as DT,
    setcontext)

from .coordinates import GeoCoordinates

def __pi() -> D:
    with localcontext() as ctx:
        ctx.traps[Inexact] = False
        ctx.prec += 2 # extra digits for intermediate steps
        three = D(3) # substitute "three=3.0" for regular floats
        lasts, t, s, n, na, d, da = 0, three, 3, 1, 0, 0, 24
        while s != lasts:
            lasts = s
            n, na = n+na, na+8
            d, da = d+da, da+32
            t = (t * n) / d
            s += t
        ctx.prec -= 2
        return D(+s) # unary plus applies the new precision

__pi_cache = defaultdict(__pi)
def pi() -> D:
    '''Compute Pi to the current precision.

    >>> print(pi())
    3.141592653589793238462643383

    '''
    return __pi_cache[getcontext().prec]

CONSTANTS_PRES = 64
with localcontext() as c:
    c.traps[Inexact] = False
    c.prec = CONSTANTS_PRES
    DEG180 = D("180")
    DEG_RAD_RATIO = pi() / DEG180
    MINUTE = D("1") / D("60")
    EQUAT_RAD_M = D("6378137")
    POLAR_RAD_M = D("6356752.314")
    SQRD_RADIAL_RATIO = (POLAR_RAD_M ** 2 / EQUAT_RAD_M ** 2)
    ELLIPSOID_ECC_SQRD = 1 - SQRD_RADIAL_RATIO
    DECIMAL0 = D("0")
    DECIMAL1 = D("1")
    DECIMAL2 = D("2")
    DECIMAL3 = D("3")
    DECIMAL60 = D("60")
    DECIMAL0_1 = D("0.1")

def setup_common_context(
    pres: int = 24,
    rounding: str = ROUND_HALF_EVEN):
    '''
    Sets up common global context
    '''
    ctx = DefaultContext
    ctx.traps[Overflow] = True
    ctx.traps[DivisionByZero] = True
    ctx.traps[InvalidOperation] = True
    ctx.traps[FloatOperation] = True
    ctx.traps[Inexact] = True
    ctx.rounding = rounding
    ctx.prec = pres
    setcontext(ctx)

def geodethic_to_ecef(point: GeoCoordinates) -> Tuple[D, D, D]:
    '''
    Function to convert from Geodethic coordinates
    to Earth Centered - Earth Fixed (ECEF) coordinate system
    ref: https://en.wikipedia.org/wiki/Geographic_coordinate_conversion#From_geodetic_to_ECEF_coordinates '''#pylint: disable=line-too-long

    lat = point.lat
    lon = point.lon
    alt = point.alt

    prime_vert_rad = EQUAT_RAD_M / D.sqrt(1 - ELLIPSOID_ECC_SQRD * sin(deg2rad(lat)))

    x_coord = (prime_vert_rad + alt) * cos(deg2rad(lat)) * cos(deg2rad(lon))
    y_coord = (prime_vert_rad + alt) * cos(deg2rad(lat)) * sin(deg2rad(lon))
    z_coord = (SQRD_RADIAL_RATIO * prime_vert_rad + alt) * sin(deg2rad(lat))

    return x_coord, y_coord, z_coord

def exp(x: D) -> D:
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
        return D(+s)

def cos(x: D) -> D:
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
        return D(+s)

def sin(x: D) -> D:
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

def deg2rad(deg: D) -> D:
    '''
    Convert from degrees to radians
    '''
    return deg * DEG_RAD_RATIO

def distance(p0: Tuple[D, ...], p1: Tuple[D, ...]) -> D:
    '''
    Calculates the cartesian distance between two points
    '''
    if len(p0) != len(p1):
        raise ValueError('both tuples must be of equal length')
    return D.sqrt(D(sum((x - y) ** DECIMAL2 for x, y in zip(p0, p1))))

def adjust(dec: D, leftexp: int = -1, rightexp: int = -3) -> D:
    '''
    Drop trailing zeros on decimal value

    leftexp: max exponent
    rightexp: min exponent
    '''
    if leftexp < rightexp:
        raise ValueError('rightexp must be greated than leftexp')

    with localcontext() as ctx:
        ctx.traps[Inexact] = False
        ctx.rounding = ROUND_DOWN
        quantized = dec.quantize(DECIMAL1.scaleb(rightexp))

    sign, digits, exponent = quantized.normalize().as_tuple()
    if exponent >= leftexp:
        rzeros = abs(exponent - leftexp)
        digits += (0,) * rzeros
        exponent = leftexp
    elif exponent < rightexp:
        drop = abs(exponent - rightexp)
        digits = digits[:-drop]
        exponent = rightexp
    ctx = getcontext()
    return D(DT(sign, digits, exponent))

# pylint: disable=too-many-locals,too-many-arguments
def moneyfmt(value, places=2, curr='', sep=',', dp='.',
             pos='', neg='-', trailneg=''):
    '''Convert Decimal to a money formatted string.

    places:  required number of places after the decimal point
    curr:    optional currency symbol before the sign (may be blank)
    sep:     optional grouping separator (comma, period, space, or blank)
    dp:      decimal point indicator (comma or period)
             only specify as blank when places is zero
    pos:     optional sign for positive numbers: '+', space or blank
    neg:     optional sign for negative numbers: '-', '(', space or blank
    trailneg:optional trailing minus indicator:  '-', ')', space or blank

    >>> d = Decimal('-1234567.8901')
    >>> moneyfmt(d, curr='$')
    '-$1,234,567.89'
    >>> moneyfmt(d, places=0, sep='.', dp='', neg='', trailneg='-')
    '1.234.568-'
    >>> moneyfmt(d, curr='$', neg='(', trailneg=')')
    '($1,234,567.89)'
    >>> moneyfmt(Decimal(123456789), sep=' ')
    '123 456 789.00'
    >>> moneyfmt(Decimal('-0.02'), neg='<', trailneg='>')
    '<0.02>'

    '''
    q = D(10) ** -places      # 2 places --> '0.01'
    sign, digits, _ = value.quantize(q).as_tuple()
    result = []
    digits = list(map(str, digits))
    build, next_ = result.append, digits.pop
    if sign:
        build(trailneg)
    for i in range(places):
        build(next_() if digits else '0')
    if places:
        build(dp)
    if not digits:
        build('0')
    i = 0
    while digits:
        build(next_())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(curr)
    build(neg if sign else pos)
    return ''.join(reversed(result))

def dec_to_str(dec: D) -> str:
    '''
    Convert the given float to a string,
    without resorting to scientific notation
    '''
    return format(dec, 'f')
