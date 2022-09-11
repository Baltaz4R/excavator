import RPi.GPIO

class Led:

    def __init__(self, pin: int):

        RPi.GPIO.setmode(RPi.GPIO.BCM) # Broadcom pin-numbering scheme.

        self.pin = pin

        RPi.GPIO.setup(pin, RPi.GPIO.OUT)
        RPi.GPIO.output(pin, RPi.GPIO.HIGH)

    def on(self) -> None:
        RPi.GPIO.output(self.pin, RPi.GPIO.LOW)

    def off(self) -> None:
        RPi.GPIO.output(self.pin, RPi.GPIO.HIGH)

    def exit(self) -> None:
        RPi.GPIO.cleanup()