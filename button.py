import time

import RPi.GPIO

class Button:
    __stop__ = False

    def __init__(self, pin: int, led: int = None):

        RPi.GPIO.setmode(RPi.GPIO.BCM) # Broadcom pin-numbering scheme.

        self.pin = pin
        self.led = led

        RPi.GPIO.setup(pin, RPi.GPIO.IN, RPi.GPIO.PUD_DOWN)

        if self.led is not None:
            RPi.GPIO.setup(led, RPi.GPIO.OUT)
            RPi.GPIO.output(led, RPi.GPIO.HIGH)

    def led_on(self) -> None:
        if self.led is None:
            return

        RPi.GPIO.output(self.led, RPi.GPIO.LOW)

    def led_off(self) -> None:
        if self.led is None: 
            return

        RPi.GPIO.output(self.led, RPi.GPIO.HIGH)

    def start(self, callback: object = None) -> None:
        self.callback = callback

        RPi.GPIO.add_event_detect(self.pin, RPi.GPIO.FALLING, callback = self.run, bouncetime = 300)

    def stop(self) -> None:
        self.__stop__ = True

    def resume(self) -> None:
        self.__stop__ = False

    def run(self, _) -> None:
        time.sleep(0.05)

        if RPi.GPIO.input(self.pin) and self.__stop__ is False:
            if self.callback is not None:
                self.callback()

            pass

    def exit(self) -> None:
        RPi.GPIO.cleanup()