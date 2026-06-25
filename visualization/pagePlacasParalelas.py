from PySide6.QtCore import Qt
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
    QSlider,
    QFrame
)
from visualization.viewer import Viewer
class PagePlacasParalelas(QWidget):
    def __init__(self,voltar):
        super().__init__()
        self.voltar = voltar
        self.dx=1
        self.dy = 1
        self.dz = 1
        self.sx = self.dx
        self.sy = self.dy
        self.sz = self.dz
        self.setup()
        self.updateMalha()
        self.updateViewr()





    def updateMalha(self):
        self.malha=Malha( self.dx, self.dy, self.dz, self.sx, self.sy, self.sz,"z")




    def setup(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        control_panel = self.createControlPanel()
        self.plotter = QtInteractor(self)
        self.plotter.add_axes(
            xlabel="X",
            ylabel="Y",
            zlabel="Z",
            line_width=3,
            interactive=True
        )
        #control_panel.setStyleSheet("background-color: #1E1E1E;")
        self.plotter.setStyleSheet("background-color: #2B2B2B;")
        main_layout.addWidget(control_panel, 1)
        main_layout.addWidget(self.plotter, 2)



    def createControlPanel(self):
        panel = QFrame()
        panel.setObjectName("controlPanel")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(12)
        layout.setContentsMargins(25, 25, 25, 25)

        panel.setLayout(layout)


        #elementos

        title = QLabel("Placas Paralelas")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("panelTitle")

        section_mesh = QLabel("Divisões da Malha")
        section_mesh.setObjectName("sectionTitle")

        section_size = QLabel("Dimensões Físicas")
        section_size.setObjectName("sectionTitle")
        #Divisões da Malha
        layout.addWidget(title)
        layout.addSpacing(20)

        layout.addWidget(section_mesh)

        layout.addWidget(self.createInputInt("Div-x", 1, 50, self.dx,self.updateDx))

        layout.addWidget(self.createInputInt("Div-y", 1, 50, self.dy, self.updateDy))

        layout.addWidget(self.createInputInt("Div-z", 1, 50, self.dz, self.updateDz))



        layout.addSpacing(20)
        # Divisões  Físicas


        layout.addWidget(section_size)


        layout.addWidget(self.createInputFloat("Size-x", 0.1, 50, self.sx, self.updateSx))

        layout.addWidget(self.createInputFloat("Size-y", 0.1, 50, self.sy, self.updateSy))

        layout.addWidget(self.createInputFloat("Size-xz", 0.1, 50, self.sz, self.updateSz))


        layout.addStretch()
        btn_voltar=self.createButton( "Voltar"  , self.voltar )
        #btn_Exportar=self.createButton( "Exportar",self.export)
        layout.addWidget(btn_voltar)
        #layout.addWidget(btn_Exportar)

        panel.setStyleSheet("""
                #controlPanel {
                    background-color: #111318;
                    border-right: 1px solid #334155;
                }

                #panelTitle {
                    color: white;
                    font-size: 26px;
                    font-weight: bold;
                }

                #sectionTitle {
                    color: #93C5FD;
                    font-size: 18px;
                    font-weight: bold;
                }

                QLabel {
                    color: white;
                    font-size: 15px;
                }
            """)
        return panel

    def createButton(self, text, function):
        button = QPushButton(text)
        button.setFixedSize(320, 50)
        button.clicked.connect(function)

        button.setStyleSheet("""
               QPushButton {
                   background-color: rgba(245, 245, 245,120);
                   color: Black;
                   font-size: 18px;
                   border-radius: 8px;
                   padding: 8px;
               }

               QPushButton:hover {
                   background-color: rgba(70, 144, 218, 230);
               }
           """)
        return button

    def createInputInt(self, text, min_value, max_value, value, function):
        row = QWidget()
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)
        row.setLayout(row_layout)

        label = QLabel(text)
        label.setFixedWidth(40)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_value)
        slider.setMaximum(max_value)
        slider.setValue(value)

        spin_box = QSpinBox()
        spin_box.setMinimum(min_value)
        spin_box.setMaximum(max_value)
        spin_box.setValue(value)
        spin_box.setFixedWidth(80)

        slider.valueChanged.connect(spin_box.setValue)
        spin_box.valueChanged.connect(slider.setValue)
        spin_box.valueChanged.connect(function)

        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #1E293B;
                border-radius: 3px;
            }

            QSlider::handle:horizontal {
                background: #3B82F6;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }

            QSlider::sub-page:horizontal {
                background: #3B82F6;
                border-radius: 3px;
            }

            QSlider::add-page:horizontal {
                background: #334155;
                border-radius: 3px;
            }
        """)

        spin_box.setStyleSheet("""
            QSpinBox {
                background-color: #111827;
                color: white;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 4px;
            }

            QSpinBox:focus {
                border: 2px solid #3B82F6;
                background-color: #0F172A;
            }

            QSpinBox::up-button,
            QSpinBox::down-button {
                background-color: #1E293B;
                border: none;
                width: 16px;
            }

            QSpinBox::up-button:hover,
            QSpinBox::down-button:hover {
                background-color: #3B82F6;
            }
        """)

        row_layout.addWidget(label)
        row_layout.addWidget(slider)
        row_layout.addWidget(spin_box)

        return row

    def createInputFloat(self, text, min_value, max_value, value, function):
        row = QWidget()
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)
        row.setLayout(row_layout)

        label = QLabel(text)
        label.setFixedWidth(40)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_value)
        slider.setMaximum(max_value)
        slider.setValue(value)

        spin_box = QDoubleSpinBox()
        spin_box.setMinimum(min_value)
        spin_box.setMaximum(max_value)
        spin_box.setDecimals(1)
        spin_box.setSingleStep(0.1)
        spin_box.setValue(value)
        spin_box.setFixedWidth(80)


        slider.valueChanged.connect(spin_box.setValue)
        spin_box.valueChanged.connect(slider.setValue)
        spin_box.valueChanged.connect(function)

        slider.setStyleSheet("""
               QSlider::groove:horizontal {
                   height: 6px;
                   background: #1E293B;
                   border-radius: 3px;
               }

               QSlider::handle:horizontal {
                   background: #3B82F6;
                   width: 16px;
                   height: 16px;
                   margin: -5px 0;
                   border-radius: 8px;
               }

               QSlider::sub-page:horizontal {
                   background: #3B82F6;
                   border-radius: 3px;
               }

               QSlider::add-page:horizontal {
                   background: #334155;
                   border-radius: 3px;
               }
           """)

        spin_box.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #111827;
                color: white;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 4px;
            }

            QDoubleSpinBox:focus {
                border: 2px solid #3B82F6;
                background-color: #0F172A;
            }

            QDoubleSpinBox::up-button,
            QDoubleSpinBox::down-button {
                background-color: #1E293B;
                border: none;
                width: 16px;
            }

            QDoubleSpinBox::up-button:hover,
            QDoubleSpinBox::down-button:hover {
                background-color: #3B82F6;
            }
        """)

        row_layout.addWidget(label)
        row_layout.addWidget(slider)
        row_layout.addWidget(spin_box)

        return row

    def updateDx(self, value):

        self.dx = value
        self.updateMalha()
        self.updateViewr()

    def updateDy(self, value):
        self.dy = value
        self.updateMalha()
        self.updateViewr()
        self.plotter.render()
    def updateDz(self, value):
        self.dz = value
        self.updateMalha()
        self.updateViewr()

    def updateSx(self, value):

        self.sx = value
        self.updateMalha()
        self.updateViewr()
    def updateSy(self, value):
        self.sy = value
        self.updateMalha()
        self.updateViewr()
    def updateSz(self, value):
        self.sz = value
        self.updateMalha()
        self.updateViewr()
    def updateViewr(self):

        self.plotter.clear()
        Viewer.tetrahedron(self.plotter, self.malha.getTetraedrosList(), self.malha.getPointsList(),"Blue")

        self.plotter.render()
    def export(self):
        pass

