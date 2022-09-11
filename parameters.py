class Angle:
    ORIGINAL_STEP = 2.0
    ORIGINAL_MAX = 14.1
    ORIGINAL_MIN = -19.52

    DISPLAY_STEP = 0.5
    DISPLAY_MAX = 14.0
    DISPLAY_MIN = -19.5

    MEDIAN = 0.0

    def convert(self, display: float) -> float:
        original = round(display / 2) * 2

        # Min and max.
        original = max(self.ORIGINAL_MIN, original) # Min.
        if original >= self.DISPLAY_MAX: original = self.ORIGINAL_MAX # Max.

        return original


class Depth:
    ORIGINAL_STEP = 0.1
    ORIGINAL_MAX = 0.9
    ORIGINAL_MIN = 0.4

    DISPLAY_STEP = 5
    DISPLAY_MAX = 90
    DISPLAY_MIN = 40

    MEDIAN = 50

    @staticmethod
    def convert(display: float) -> float:
        return display // 10 / 10


class Velocity1:
    ORIGINAL_STEP = 4
    ORIGINAL_MAX = 40
    ORIGINAL_MIN = 4

    DISPLAY_STEP = 5
    DISPLAY_MAX = 100
    DISPLAY_MIN = 10

    MEDIAN = 50

    @staticmethod
    def convert(display: float) -> float:
        return display // 10 * 4


class Velocity2:
    ORIGINAL_STEP = 1
    ORIGINAL_MAX = 1000
    ORIGINAL_MIN = 600

    DISPLAY_STEP = 1
    DISPLAY_MAX = 1000
    DISPLAY_MIN = 600

    MEDIAN = 800

    @staticmethod
    def convert(display: float) -> float:
        return display