import enum
from PyQt6.QtGui import QFont


class FontWeight(enum.Enum):
    NORMAL = ("Normal", 0, QFont.Weight.Normal)
    THIN = ("Thin", 1, QFont.Weight.Thin)
    EXTRA_LIGHT = ("ExtraLight", 2, QFont.Weight.ExtraLight)
    LIGHT = ("Light", 3, QFont.Weight.Light)
    MEDIUM = ("Medium", 4, QFont.Weight.Medium)
    DEMI_BOLD = ("DemiBold", 5, QFont.Weight.DemiBold)
    BOLD = ("Bold", 6, QFont.Weight.Bold)
    EXTRA_BOLD = ("ExtraBold", 7, QFont.Weight.ExtraBold)
    BLACK = ("Black", 8, QFont.Weight.Black)

    def __init__(self, label: str, index: int, weight: QFont.Weight):
        self.label = label
        self.index = index
        self.weight = weight

    @classmethod
    def from_label(cls, label: str):
        for e in cls:
            if e.label == label:
                return e
        raise ValueError(f"{label} is not a valid font label!")

    @classmethod
    def from_index(cls, index: int):
        for e in cls:
            if e.index == index:
                return e
        raise ValueError(f"{index} is not a valid font index!")

    @classmethod
    def from_label_to_weight(cls, label: str):
        return cls.from_label(label).weight

    @classmethod
    def from_label_to_index(cls, label: str):
        return cls.from_label(label).index