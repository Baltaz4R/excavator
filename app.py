import os
import sys
import time
import json
import glob
import pathlib

from PyQt5.QtWidgets import QApplication

from led import Led
from window import Window
from button import Button
from counter import Counter
from parameters import Angle, Depth, Velocity1, Velocity2


# Pins.
# Display 1.
DISPLAY0_CLK = 13
DISPLAY0_DIO = 6
DISPLAY0_INC = 14
DISPLAY0_DEC = 15
# Display 2.
DISPLAY1_CLK = 16
DISPLAY1_DIO = 12
DISPLAY1_INC = 18
DISPLAY1_DEC = 23
# Display 3.
DISPLAY2_CLK = 26
DISPLAY2_DIO = 19
DISPLAY2_INC = 24
DISPLAY2_DEC = 25
# Display 4.
DISPLAY3_CLK = 21
DISPLAY3_DIO = 20
DISPLAY3_INC = 8
DISPLAY3_DEC = 7
# Start button.
START_PIN = 9
START_LED = 22
# Stop button.
STOP_PIN = 5
STOP_LED = 10
# AMPd button.
AMPD_PIN = 4
AMPD_LED = 27
# Shutdown button.
SHUTDOWN_PIN = 11
# Warning led.
WARNING_LED = 17

# Parameters.
PARAM0 = Angle()
PARAM1 = Depth()
PARAM2 = Velocity1()
PARAM3 = Velocity2()

# Keys.
GREEN_ZONES = 'zelene zone'
RED_ZONES = 'crvene zone'

# Path to files.
PATH = glob.glob('/media/pi/*')[0] if len(glob.glob('/media/pi/*')) > 0 else ''



if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = Window()

    is_ampd_button_pressed = False

    start_button = Button(START_PIN, START_LED)
    stop_button = Button(STOP_PIN, STOP_LED)
    ampd_button = Button(AMPD_PIN, AMPD_LED)
    # shutdown_button = Button(SHUTDOWN_PIN)

    warning_led = Led(WARNING_LED)

    counters = [
        Counter(window.displays[0], DISPLAY0_CLK, DISPLAY0_DIO, DISPLAY0_INC, DISPLAY0_DEC),
        Counter(window.displays[1], DISPLAY1_CLK, DISPLAY1_DIO, DISPLAY1_INC, DISPLAY1_DEC),
        Counter(window.displays[2], DISPLAY2_CLK, DISPLAY2_DIO, DISPLAY2_INC, DISPLAY2_DEC),
        Counter(window.displays[3], DISPLAY3_CLK, DISPLAY3_DIO, DISPLAY3_INC, DISPLAY3_DEC),
    ]

    counters[0].start(PARAM0.MEDIAN, PARAM0.DISPLAY_STEP, PARAM0.DISPLAY_MIN, PARAM0.DISPLAY_MAX)
    counters[1].start(PARAM1.MEDIAN, PARAM1.DISPLAY_STEP, PARAM1.DISPLAY_MIN, PARAM1.DISPLAY_MAX)
    counters[2].start(PARAM2.MEDIAN, PARAM2.DISPLAY_STEP, PARAM2.DISPLAY_MIN, PARAM2.DISPLAY_MAX)
    counters[3].start(PARAM3.MEDIAN, PARAM3.DISPLAY_STEP, PARAM3.DISPLAY_MIN, PARAM3.DISPLAY_MAX)

    def on_shutdown():
        start_button.exit()
        stop_button.exit()
        ampd_button.exit()
        # shutdown_button.exit()

        warning_led.exit()

        for counter in counters:
            counter.exit()

        os.system('shutdown now -h')

    def on_start():
        start_button.stop()
        ampd_button.stop()

        for counter in counters:
            counter.stop()

        start_button.led_on()

        filename = str(PARAM0.convert(counters[0].number)) + '_' + str(PARAM2.convert(counters[2].number)) + '_' + str(PARAM1.convert(counters[1].number))
        filepath = f'{PATH}/parameters/{filename}.json'

        if not pathlib.Path(filepath).is_file():
            window.show_message('File Error', f"The file '{filename}' does not exist.")
            on_shutdown()

        with open(filepath, 'r') as file:
            data = json.load(file)

        global is_ampd_button_pressed

        green_zones = list(data[GREEN_ZONES].values()) if is_ampd_button_pressed else list(data[GREEN_ZONES].values()) + list(data[RED_ZONES].values())
        red_zones = list(data[RED_ZONES].values()) if is_ampd_button_pressed else []

        cursor = PARAM3.convert(counters[3].number)

        window.plot(cursor, green_zones, red_zones)

        if is_ampd_button_pressed:

            min(red_zones + green_zones, key = lambda zone : zone[0])[0] = float('-inf')
            max(red_zones + green_zones, key = lambda zone : zone[1])[1] = float('inf')

            for lower, upper in red_zones:
                if lower <= cursor <= upper:
                    warning_led.on()

                    cursor = min(lower, upper, key = lambda edge : abs(edge - cursor))

                    window.move(cursor)

                    counters[3].number = cursor
                    counters[3].write(cursor)

                    warning_led.off()

                    break

        for lower, upper in green_zones:
            if lower <= cursor <= upper:
                rpm_value = None

                for file in glob.glob(f'{PATH}/videos/left/rot_*.gif'):
                    words = pathlib.Path(file).stem.split('_')

                    if len(words) > 1 and lower <= int(words[1]) <= upper:
                        rpm_value = int(words[1])
                        break

                if rpm_value is None:
                    window.show_message('File Error', "The gif files do not exist.")
                    on_shutdown()

                filenames = ['rot_' + str(rpm_value), str(rpm_value) + '_' + str(PARAM0.convert(counters[0].number))]
                filepaths = [f'{PATH}/videos/left/{filenames[0]}.gif', f'{PATH}/videos/right/{filenames[1]}.gif']

                window.play(filepaths[0], 0)
                window.play(filepaths[1], 1)

                break

        stop_button.resume()

    def on_stop():
        stop_button.stop()

        start_button.led_off()

        for _ in range(2):
            stop_button.led_on()
            time.sleep(1)

            stop_button.led_off()
            time.sleep(1)

        window.clear()

        for counter in counters:
            counter.resume()

        start_button.resume()
        ampd_button.resume()

    def on_ampd():
        global is_ampd_button_pressed

        if is_ampd_button_pressed:
            ampd_button.led_off()
            is_ampd_button_pressed = False

        else:
            ampd_button.led_on()
            is_ampd_button_pressed = True

    start_button.start(on_start)
    stop_button.start(on_stop)
    ampd_button.start(on_ampd)
    # shutdown_button.start(on_shutdown)

    stop_button.stop()

    if PATH == '':
        window.show_message('File Error', 'Path to essential files does not exist.' + '\n' + 'Check if USB is inserted.')
        on_shutdown()

    sys.exit(app.exec_())