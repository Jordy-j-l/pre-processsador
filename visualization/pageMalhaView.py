from pyvistaqt import QtInteractor

from mesh.Builder import Malha
import numpy
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QStackedWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QFrame
)
class PageMalhaView(QWidget):
    def __init__(self):
        super().__init__()
        self.dx=1
        self.dy = 1
        self.dz = 1
        self.sx = self.dx
        self.sy = self.dy
        self.sz = self.dz
        self.setup()






    def setMalha(self):
        self.malha=Malha( self.dx, self.dy, self.dz, self.sx, self.sy, self.sz,"z")

    def setup(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        control_panel = QFrame()
        control_layout = QVBoxLayout()

        control_panel.setLayout(control_layout)
        title = QLabel("Placas Paralelas")
        control_layout.addWidget(title)

        self.plotter = QtInteractor(self)

        control_panel.setStyleSheet("background-color: #1E1E1E;")
        self.plotter.setStyleSheet("background-color: #2B2B2B;")
        main_layout.addWidget(control_panel, 1)
        main_layout.addWidget(self.plotter, 2)