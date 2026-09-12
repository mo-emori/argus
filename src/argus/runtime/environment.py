from enum import Enum


class Environment(str, Enum):
    TEST = "TEST"
    PAPER = "PAPER"
    LIVE = "LIVE"