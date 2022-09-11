import time
import math
import tm1637

import RPi.GPIO

from threading import Thread, Event


class Counter(Thread):
    __exit__ = False

    def __init__(self, display_win: object, display_clk: int, display_dio: int, inc_pin: int, dec_pin: int):
        Thread.__init__(self)

        self.__stop__ = Event()
        self.__stop__.set()

        self.__pressed__ = Event()
        self.__pressed__.clear()

        self.window = display_win

        self.display_clk = display_clk
        self.display_dio = display_dio

        self.display = tm1637.TM1637(clk = display_clk, dio = display_dio)

        RPi.GPIO.setmode(RPi.GPIO.BCM) # Broadcom pin-numbering scheme.

        self.inc_pin = inc_pin
        self.dec_pin = dec_pin

        RPi.GPIO.setup(inc_pin, RPi.GPIO.IN, RPi.GPIO.PUD_DOWN)
        RPi.GPIO.setup(dec_pin, RPi.GPIO.IN, RPi.GPIO.PUD_DOWN)

        RPi.GPIO.add_event_detect(inc_pin, RPi.GPIO.FALLING, callback = lambda _ : self.__pressed__.set(), bouncetime = 300)
        RPi.GPIO.add_event_detect(dec_pin, RPi.GPIO.FALLING, callback = lambda _ : self.__pressed__.set(), bouncetime = 300)

    def write(self, number: float = None) -> None:
        if number is None: number = self.number

        if isinstance(number, float):
            number = max(-99.9, min(number, 999.9))
            frac, whole = math.modf(number)

            segments = [self.display.encode_char('-')] if number < 0 else [] # Sign.
            segments += [self.display.encode_char(char) for char in str(abs(int(whole)))] # Whole.
            segments += [self.display.encode_char(str(abs(int(10 * frac))))] # Frac.

            segments[-2] |= 0x80 # Dot.

            while len(segments) < 4: segments.insert(0, 0)

            self.display.write(segments)
            self.window.display(str(number))

        else:
            self.display.number(number)
            self.window.display(number)

    def start(self, number: float, step: float, min: float, max: float) -> None:
        if isinstance(step, float):
            number = float(number)

        self.number = number
        self.step = step
        self.min = min
        self.max = max

        self.write()

        self.__pressed__.clear()

        Thread.start(self)

    def stop(self) -> None:
        self.__stop__.clear()

    def resume(self) -> None:
        self.__stop__.set()

    def run(self) -> None:

        while not self.__exit__:

            self.__stop__.wait()

            self.__pressed__.wait()
            self.__pressed__.clear()

            time.sleep(0.05)

            sleep_time = 0.25

            is_inc = RPi.GPIO.input(self.inc_pin)
            is_dec = RPi.GPIO.input(self.dec_pin)

            while (is_inc or is_dec) and self.__stop__.is_set():
                self.number = min(self.number + self.step, self.max) if is_inc else max(self.number - self.step, self.min)

                self.write()

                time.sleep(sleep_time)

                sleep_time = max(sleep_time - 0.015, 0.03)

                is_inc = RPi.GPIO.input(self.inc_pin)
                is_dec = RPi.GPIO.input(self.dec_pin)

    def exit(self) -> None:
        if self.is_alive():
            self.__exit__ = True

            self.__stop__.set()
            self.__pressed__.set()

        self.display.write([0, 0, 0, 0])

        RPi.GPIO.cleanup()