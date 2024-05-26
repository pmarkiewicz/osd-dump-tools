from dataclasses import dataclass
from array import array


@dataclass(slots=True)
class Frame:
    idx: int
    next_idx: int
    size: int
    data: array

@dataclass(slots=True)
class SrtFrame:
    start_time: float
    idx: int
    signal: int
    ch: int
    flighttime: int
    delay: int
    bitrate: float
    distance: int = 0
    sbat: float = 0
    gbat: float = 0
    uavbat: float = 0
    glsbat: float = 0
    uavbatcells: int = 0
    glsbatcells: int = 0
    rcsignal: int = 0
