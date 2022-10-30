from enum import Enum


class GardenEnclosure(str, Enum):
    INDOOR = "INDOOR"
    OUTDOOR = "OUTDOOR"