''' Generic events '''

import uuid

from dataclasses import dataclass
from typing import Mapping

@dataclass(order=True)
class MetricsReport:
    ''' Generic event schema, used for common schema non-specific logging '''
    metrics: Mapping
    report_id: uuid.UUID
    frequency: int
    schema_ver: int = 1
