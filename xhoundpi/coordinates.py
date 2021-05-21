'''
Defines geographic coordinates model
'''

from dataclasses import dataclass
from decimal import Decimal

@dataclass
class GeoCoordinates:
    '''
    Model for geographic coordinates offsets
    '''
    lat: Decimal
    lon: Decimal
    alt: Decimal
