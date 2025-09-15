from dataclasses import dataclass
from typing import Optional, Union
from dataclasses_json import dataclass_json

from ..enums.overall_fit_level import OverallFitLevel as OverallFitLevelEnum


@dataclass_json
@dataclass
class Relevance:
    TitleMatch: Optional[float] = None
    ResponsibilityMatch: Optional[float] = None
    OverallFit: Optional[Union[float, OverallFitLevelEnum]] = None