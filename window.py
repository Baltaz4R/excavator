import os
import sys
import time
import matplotlib

import matplotlib.pyplot
import matplotlib.backends.backend_qt5agg

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QLabel, QVBoxLayout, QGridLayout


class Window(QWidget):
    NUMBER_OF_DISPLAYS = 4
    NUMBER_OF_DIGITS = 4

    __play_signal__ = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle('AMPd')
        self.setWindowIcon(QtGui.QIcon(os.path.dirname(__file__) + '/assets/rotodyna.jpg'))
        self.setCursor(QtCore.Qt.BlankCursor)
        self.setStyleSheet("background-color: white;") # rgb(180, 150, 50)
        self.setGeometry(0, 0, QtWidgets.QDesktopWidget().screenGeometry(-1).width(), QtWidgets.QDesktopWidget().screenGeometry(-1).height())

        self.showFullScreen()
        self.show()

        self.__play_signal__.connect(self.__play__)

        outerLayout = QVBoxLayout()
        moviesLayout = QGridLayout()
        displaysLayout = QGridLayout()

        # Init displays.
        self.displays = [QtWidgets.QLCDNumber(self) for _ in range(self.NUMBER_OF_DISPLAYS)]

        area_width = int(self.width() / self.NUMBER_OF_DISPLAYS)
        digit_width = int(area_width / (self.NUMBER_OF_DIGITS + 4))

        width = self.NUMBER_OF_DIGITS * digit_width
        height = int(self.height() / 9)

        for index, display in enumerate(self.displays):
            # display.move(index * area_width + 2 * digit_width, int(self.height() / 2))
            displaysLayout.addWidget(display, 0, index, alignment = QtCore.Qt.AlignBottom)

            display.setMinimumWidth(width)
            display.setMinimumHeight(height)

            display.setMaximumWidth(width)
            display.setMaximumHeight(height)

            display.setStyleSheet("background-color: rgb(0, 20, 40); color: rgb(15, 155, 255);")

            display.show()

        displaysLayout.setContentsMargins(0, 0, 0, int(self.height() / 54))

        # Init gif.
        self.movies = [QLabel(), QLabel()]

        self.movies[0].filename = None
        self.movies[1].filename = None

        self.movies[0].qmovie = None
        self.movies[1].qmovie = None

        self.movies[0].setMinimumWidth(int(self.width() / 2) - height)
        self.movies[0].setMinimumHeight(int(16 * self.height() / 27))
        self.movies[1].setMinimumWidth(int(self.width() / 2) - height)
        self.movies[1].setMinimumHeight(int(16 * self.height() / 27))

        moviesLayout.addWidget(self.movies[0], 0, 0, alignment = QtCore.Qt.AlignLeft)
        moviesLayout.addWidget(self.movies[1], 0, 1, alignment = QtCore.Qt.AlignRight)

        moviesLayout.setContentsMargins(int(height / 2), 0, int(height / 2), 0)

        # Init canvas.
        self.cursor = None

        self.figure = matplotlib.pyplot.figure()
        self.figure.set_facecolor('none')

        self.canvas = matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg(self.figure)
        self.canvas.setMaximumHeight(2 * int(self.height() / 9))

        outerLayout.addWidget(self.canvas, alignment = QtCore.Qt.AlignTop)
        outerLayout.addLayout(moviesLayout)
        outerLayout.addLayout(displaysLayout)

        self.setLayout(outerLayout)

    def show_message(self, title: str, text: str) -> None:
        dialog = QDialog(self)

        dialog.setCursor(QtCore.Qt.BlankCursor)
        dialog.setWindowTitle(title)

        width = int(self.width() / 6)
        height = int(self.height() / 12)

        dialog.setMinimumWidth(width)
        dialog.setMinimumHeight(height)

        layout = QGridLayout()

        icon = QLabel(self)
        label = QLabel(text)

        icon.setPixmap(QtGui.QPixmap(os.path.dirname(__file__) + '/assets/icon.png').scaled(64, 64))
        label.setStyleSheet("font-size: 15pt;")

        layout.addWidget(icon, 0, 0, alignment = QtCore.Qt.AlignTop)
        layout.addWidget(label, 0, 1, alignment = QtCore.Qt.AlignTop)

        dialog.setLayout(layout)

        QtCore.QTimer.singleShot(5000, dialog.close)

        dialog.exec()

    def plot(self, cursor: float, green_zones: list, red_zones: list) -> None:
        self.figure.clear()

        ax = self.figure.add_subplot()

        for zone in green_zones:
            ax.axvspan(zone[0], zone[1], alpha = 0.5, color = 'green', lw = 0)

        for zone in red_zones:
            ax.axvspan(zone[0], zone[1], alpha = 0.5, color = 'red', lw = 0)

        matplotlib.pyplot.xlim(min(green_zones + red_zones, key = lambda zone: zone[0])[0], max(green_zones + red_zones, key = lambda zone: zone[1])[1])
        matplotlib.pyplot.ylim(0, 2)

        self.cursor = matplotlib.pyplot.vlines(cursor, 0, 10, 'yellow', linewidth = 5)

        ax.get_yaxis().set_visible(False)
        ax.set_aspect((ax.get_xlim()[1] - ax.get_xlim()[0]) / (ax.get_ylim()[1] - ax.get_ylim()[0]) / 10)
        ax.set_title('The working rpm spectrum of the BWE SchRs 1600.')

        self.canvas.draw()

    def move(self, cursor: float) -> None:
        if self.cursor is None:
            return

        start = int(self.cursor.get_segments()[0][0][0])
        end = int(cursor)
        step = 1 if end > start else -1

        for value in range(start + step, end + step, step):
            self.cursor.remove()
            self.cursor = matplotlib.pyplot.vlines(value, 0, 10, 'yellow', linewidth = 5)

            self.canvas.draw()

            time.sleep(0.05)

    def __play__(self) -> None:
        for movie in self.movies:
            if movie.qmovie is not None:
                movie.qmovie.stop()
                del movie.qmovie
                movie.qmovie = None

            if movie.filename is None:
                continue

            movie.qmovie = QtGui.QMovie(movie.filename)

            movie.qmovie.jumpToFrame(0)
            size = movie.qmovie.currentImage().size()
            size.scale(movie.width(), movie.height(), QtCore.Qt.KeepAspectRatio)
            movie.qmovie.setScaledSize(size)

            movie.qmovie.start()

            movie.setMovie(movie.qmovie)

    def play(self, filename: str, position: int) -> None:
        self.movies[position].filename = filename

        self.__play_signal__.emit()

    def clear(self) -> None:
        self.figure.clear()
        self.canvas.draw()

        self.movies[0].filename = None
        self.movies[1].filename = None

        self.__play_signal__.emit()

        self.movies[0].clear()
        self.movies[1].clear()

    def set_on_display(self, index: int, number: float) -> None:
        self.displays[index].display(number)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = Window()

    window.plot(800, [[716, 766], [799, 867], [903, 1000]], [[600, 716], [766, 799], [867, 903]])

    sys.exit(app.exec_())