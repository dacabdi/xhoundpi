''' Encodes human input events, their sources, their types, and any additional context '''

from dataclasses import dataclass
from enum import Enum
from typing import Any

class HIType(Enum):
    ''' Types of human input events '''
    UNKOWN = -1
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    SELECT0 = 4
    SELECT1 = 5
    TOUCH = 6
    POWER = 7

class HISource(Enum):
    ''' Sources for human input events '''
    KEYBOARD = 0
    BUTTONPANEL = 1

@dataclass
class HIEvent:
    ''' Encodes human input event '''
    source: HISource
    type: HIType
    context: Any
