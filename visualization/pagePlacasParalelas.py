from PySide6.QtCore import Qt
from pyvistaqt import QtInteractor
from vtkmodules.generate_pyi import namespace_pyi

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
    QFrame,
    QScrollArea
)
from visualization.viewer import Viewer
from output.export import Export as ex




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
        self.opacity=0.6
        self.setup()
        self.updateMalha(self.sx, self.sy, self.sz)
        self.updateViewr()





    def updateMalha(self,sxf,syf,szf):
        self.malha=Malha( self.dx, self.dy, self.dz, sxf, syf, szf,"z")




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

        panel_layout = QVBoxLayout()
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)
        panel.setLayout(panel_layout)


        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        scroll_content.setObjectName("controlPanel")
        scroll_layout = QVBoxLayout()
        scroll_layout.setAlignment(Qt.AlignTop)
        scroll_layout.setSpacing(12)
        scroll_layout.setContentsMargins(25, 25, 25, 25)

        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)

        footer = QWidget()
        footer.setObjectName("controlPanel")
        footer_layout = QVBoxLayout()
        footer_layout.setContentsMargins(20, 20, 20, 20)
        footer_layout.setSpacing(12)
        footer.setLayout(footer_layout)

        panel_layout.addWidget(scroll_area)
        panel_layout.addWidget(footer)



        #elementos

        title = QLabel("Placas Paralelas")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("panelTitle")

        section_mesh = QLabel("Divisões da Malha")
        section_mesh.setObjectName("sectionTitle")

        section_size = QLabel("Dimensões Físicas")
        section_size.setObjectName("sectionTitle")
        view_setup = QLabel("View Setup")
        view_setup.setObjectName("sectionTitle")
        #Divisões da Malha
        scroll_layout.addWidget(title)
        scroll_layout.addSpacing(20)

        scroll_layout.addWidget(section_mesh)

        scroll_layout.addWidget(self.createInputInt("Div-x", 1, 50, self.dx,self.updateDx))

        scroll_layout.addWidget(self.createInputInt("Div-y", 1, 50, self.dy, self.updateDy))

        scroll_layout.addWidget(self.createInputInt("Div-z", 1, 50, self.dz, self.updateDz))



        scroll_layout.addSpacing(20)
        # Divisões  Físicas
        wsx = self.createInputFloat("Size-x", 0.1, 50, self.sx, self.updateSx)

        wsy = self.createInputFloat("Size-y", 0.1, 50, self.sy, self.updateSy)

        wsz = self.createInputFloat("Size-z", 0.1, 50, self.sz, self.updateSz)

        row = QWidget()
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)
        row.setLayout(row_layout)
        row_layout.addWidget(section_size)
        self.fix_size=QCheckBox("SYNC")
        self.fix_size.setChecked(False)
        self.fix_size.toggled.connect(
            lambda checked: self.updateFixSize(checked, wsx, wsy, wsz)
        )
        row_layout.addWidget(self.fix_size)

        scroll_layout.addWidget(row)
        scroll_layout.addWidget(wsx)
        scroll_layout.addWidget(wsy)
        scroll_layout.addWidget(wsz)

        scroll_layout.addSpacing(10)
        #viewr_setup

        scroll_layout.addWidget(view_setup)
        scroll_layout.addWidget(self.createSpinBox("Opacidade", 0.1,1.0,self.opacity, self.updateOpacity))
        row2 = QWidget()
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)
        row2.setLayout(row_layout)
        row_layout.addWidget(self.createButtonClean("View YX", self.updateViewXY))
        row_layout.addWidget(self.createButtonClean("View ZX", self.updateViewXZ))
        scroll_layout.addWidget(row2)
        row3 = QWidget()
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)
        row3.setLayout(row_layout)
        row_layout.addWidget(self.createButtonClean("View ZY", self.updateViewYZ))
        row_layout.addWidget(self.createButtonClean("View 3D", self.updateView3D))
        scroll_layout.addWidget(row3)
        #footer_layout.addStretch()
        row4 = QWidget()
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)
        row4.setLayout(row_layout)
        btn_voltar=self.createButton( "Voltar"  , self.voltar )
        btn_Exportar=self.createButton( "Exportar",self.export )
        row_layout.addWidget(btn_voltar)
        row_layout.addWidget(btn_Exportar)
        footer_layout.addWidget(row4)

        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #111318;
            }

            QScrollBar:vertical {
                background: #111318;
                width: 10px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background: #3B82F6;
                border-radius: 5px;
                min-height: 30px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
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
        button.setFixedSize(140, 50)
        button.clicked.connect(function)

        button.setStyleSheet("""
               QPushButton {
                   background-color: rgba(70, 144, 218, 230);
                   color: Black;
                   font-size: 15px;
                   border-radius: 8px;
                   padding: 6px;
               }

               QPushButton:hover {
                   background-color: rgba(245, 245, 245,120);
               }
           """)
        return button

    def createButtonClean(self, text, function):
        button = QPushButton(f"[ {text} ]")
        button.setFixedSize(140, 28)
        button.clicked.connect(function)

        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 13px;
                font-weight: bold;
                border: none;
                text-align: left;
                padding-left: 6px;
            }

            QPushButton:hover {
                color: #3B82F6;
                background-color: rgba(59, 130, 246, 30);
            }

            QPushButton:pressed {
                color: #93C5FD;
                background-color: rgba(59, 130, 246, 60);
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
        scale = 10
        row = QWidget()
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)
        row.setLayout(row_layout)

        label = QLabel(text)
        label.setFixedWidth(40)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(int(min_value ))
        slider.setMaximum(int(max_value ))
        slider.setValue(int(value))

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
    def createSpinBox(self, text, min_value, max_value, value, function):
        row = QWidget()
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)
        row.setLayout(row_layout)

        label = QLabel(text)
        #label.setFixedWidth(80)


        spin_box = QDoubleSpinBox()
        spin_box.setMinimum(min_value)
        spin_box.setMaximum(max_value)
        spin_box.setDecimals(1)
        spin_box.setSingleStep(0.1)
        spin_box.setValue(value)
        spin_box.setFixedWidth(80)


        spin_box.valueChanged.connect(spin_box.setValue)
        spin_box.valueChanged.connect(function)



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
        row_layout.addWidget(spin_box)

        return row







    def updateFixSize(self, checked, widget1, widget2, widget3):
        if checked:
            widget1.setVisible(False)
            widget2.setVisible(False)
            widget3.setVisible(False)
            self.updateAll()
        else:
            widget1.setVisible(True)
            widget2.setVisible(True)
            widget3.setVisible(True)
            self.updateAll()


    def updateDx(self, value):
        if self.fix_size.isChecked():
            self.dx = value

            self.updateMalha(self.dx, self.dy, self.dz)
        else:
            self.dx = value
            self.updateMalha(self.sx, self.sy, self.sz)

        self.updateViewr()

    def updateDy(self, value):
        if self.fix_size.isChecked():
            self.dy = value
            self.updateMalha(self.dx, self.dy, self.dz)
        else:
            self.dy = value
            self.updateMalha(self.sx, self.sy, self.sz)

        self.updateViewr()
        self.plotter.render()
    def updateDz(self, value):
        if self.fix_size.isChecked():
            self.dz = value
            self.updateMalha(self.dx, self.dy, self.dz)
        else:
            self.dz = value
            self.updateMalha(self.sx, self.sy, self.sz)

        self.updateViewr()

    def updateSx(self, value):

        self.sx = value
        self.updateMalha(self.sx, self.sy, self.sz)
        self.updateViewr()
    def updateSy(self, value):
        self.sy = value
        self.updateMalha(self.sx, self.sy, self.sz)
        self.updateViewr()
    def updateSz(self, value):
        self.sz = value
        self.updateMalha(self.sx, self.sy, self.sz)
        self.updateViewr()
    def updateAll(self):
        if self.fix_size.isChecked():
            self.dx = self.dx

            self.dy = self.dy

            self.dz = self.dz
            self.updateMalha(self.dx, self.dy, self.dz)
        else:
            self.dx = self.dx

            self.dy = self.dy

            self.dz = self.dz
            self.updateMalha(self.sx, self.sy, self.sz)

        self.updateViewr()
    def updateOpacity(self, value):
        self.opacity = value
        self.updateViewr()

    def updateViewr(self):
        print("update:",self.opacity)
        print("DX:", self.dx,"DY:", self.dy,"DZ:", self.dz,"SX:", self.sx,"SY:", self.sy,"SZ:", self.sz)
        self.plotter.clear()
        Viewer.tetrahedron(self.plotter, self.malha.getTetraedrosList(), self.malha.getPointsList(),"Blue",opacity=self.opacity)

        self.plotter.render()
    def export(self):
        exp=ex(self.malha.getTetraedrosList(),self.malha.getPointsList(),self.malha.getVetorList())

        name_e=f"elementos-Div({self.dx},{self.dy},{self.dz})-Size({self.sx},{self.sy},{self.sz})"
        name_p=f"pontos-Div({self.dx},{self.dy},{self.dz})-Size({self.sx},{self.sy},{self.sz})"
        name_v=f"vetor-Div({self.dx},{self.dy},{self.dz})-Size({self.sx},{self.sy},{self.sz})"
        exp.exportAll(name_e,name_p,name_v)


    def updateViewXY(self):
        Viewer.viewXY(self.plotter)





    def updateViewXZ(self):
        Viewer.viewXZ(self.plotter)

    def updateViewYZ(self):
        Viewer.viewYZ(self.plotter)
    def updateView3D(self):
        Viewer.view3D(self.plotter)