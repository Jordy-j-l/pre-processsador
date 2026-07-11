from PySide6.QtCore import Qt
from datetime import datetime
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
    QScrollArea,
    QMessageBox
)
from visualization.viewer import Viewer
from output.export import Export as ex




class Page1Vara(QWidget):
    def __init__(self, voltar):
        super().__init__()
        self.voltar = voltar
        self.dx=1
        self.dy = 1
        self.dz = 1
        self.sx = self.dx
        self.sy = self.dy
        self.sz = self.dz
        self.opacity = 0.6
        self.vara_ativa = False
        self.vara_e_x = 0
        self.vara_e_y = 0
        self.raio_vara = 0.00794
        self.comprimento_vara = 1.0
        self.camadas_deformadas = 6
        self.max_div = 4
        self.min_div = 1
        self.ballooning = 1.55
        self.mostrar_normais = True
        self.mostrar_deformados = True
        self.cubos_normais = None
        self.cubos_deformados = None
        self.setup()
        self.updateMalha(self.sx, self.sy, self.sz)
        self.updateViewr()





    def updateMalha(self,sxf,syf,szf):
        self.malha=Malha( self.dx, self.dy, self.dz, sxf, syf, szf)
        self.cubos_normais = None
        self.cubos_deformados = None
        if self.vara_ativa:
            pontos, cubos, normais, deformados = self.malha.gerarMalha1Vara(
                self.vara_e_x, self.vara_e_y, self.raio_vara,
                self.comprimento_vara, self.max_div, self.min_div,
                self.camadas_deformadas, self.ballooning,
            )
            self.malha.points_list = pontos
            self.malha.cube_list = cubos
            self.malha.final_points_list = pontos
            self.malha.final_cube_list = cubos
            self.cubos_normais = normais
            self.cubos_deformados = deformados




    def setup(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        control_panel = self.createControlPanel()

        self.plotter = QtInteractor()
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

        title = QLabel("Malha com uma Vara")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("panelTitle")

        section_mesh = QLabel("Divisões da Malha")
        section_mesh.setObjectName("sectionTitle")

        section_size = QLabel("Divisões Físicas")
        section_size.setObjectName("sectionTitle")
        vara_setup = QLabel("Setup Vara")
        vara_setup.setObjectName("sectionTitle")
        view_mesh = QLabel("View Malha")
        view_mesh.setObjectName("sectionTitle")
        view_setup = QLabel("View Setup")
        view_setup.setObjectName("sectionTitle")

        #Divisões da Malha
        scroll_layout.addWidget(title)
        scroll_layout.addSpacing(20)

        scroll_layout.addWidget(section_mesh)

        scroll_layout.addWidget(self.createInputInt("Div-x", 1, 20, self.dx,self.updateDx))

        scroll_layout.addWidget(self.createInputInt("Div-y", 1, 20, self.dy, self.updateDy))

        scroll_layout.addWidget(self.createInputInt("Div-z", 1, 20, self.dz, self.updateDz))



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
        setup_row = QWidget()
        setup_layout = QHBoxLayout(setup_row)
        setup_layout.setContentsMargins(0, 0, 0, 0)
        setup_layout.addWidget(vara_setup)
        self.vara_toggle = QCheckBox("OFF")
        self.vara_toggle.setChecked(False)
        self.vara_toggle.toggled.connect(self.updateVaraAtiva)
        setup_layout.addWidget(self.vara_toggle)
        scroll_layout.addWidget(setup_row)

        self.vara_config = QWidget()
        vara_config_layout = QVBoxLayout(self.vara_config)
        vara_config_layout.setContentsMargins(0, 0, 0, 0)
        vara_config_layout.setSpacing(10)
        vara_config_layout.addWidget(QLabel("Posição da Vara"))
        self.vara_x_spin = self.createLabeledIntegerInput("Eixo X", 0, self.dx - 1, self.vara_e_x, self.updateVara_e_x)
        self.vara_y_spin = self.createLabeledIntegerInput("Eixo Y", 0, self.dy - 1, self.vara_e_y, self.updateVara_e_y)
        vara_config_layout.addWidget(self.vara_x_spin)
        vara_config_layout.addWidget(self.vara_y_spin)
        vara_config_layout.addWidget(self.createPreciseFloatInput("Raio", 0.00001, 20.0, self.raio_vara, self.updateRaio, 5))
        self.comprimento_input = self.createPreciseFloatInput("Comprimento", 0.1, self.sz, self.comprimento_vara, self.updateComprimento, 2)
        vara_config_layout.addWidget(self.comprimento_input)
        vara_config_layout.addWidget(self.createLabeledIntegerInput("Camadas deformadas", 1, 20, self.camadas_deformadas, self.updateCamadas))
        self.max_div_input = self.createLabeledIntegerInput("Máximo de divisões", self.min_div, 20, self.max_div, self.updateMaxDiv)
        self.min_div_input = self.createLabeledIntegerInput("Mínimo de divisões", 1, self.max_div, self.min_div, self.updateMinDiv)
        vara_config_layout.addWidget(self.max_div_input)
        vara_config_layout.addWidget(self.min_div_input)
        vara_config_layout.addWidget(self.createPreciseFloatInput("Razão ballooning", 1.0, 10.0, self.ballooning, self.updateBallooning, 2))
        self.vara_config.setVisible(False)
        scroll_layout.addWidget(self.vara_config)

        scroll_layout.addSpacing(10)
        scroll_layout.addWidget(view_mesh)
        visibility_row = QWidget()
        visibility_layout = QHBoxLayout(visibility_row)
        visibility_layout.setContentsMargins(0, 0, 0, 0)
        visibility_layout.addWidget(self.createToggle("Normais ON", self.updateMostrarNormais, True))
        visibility_layout.addWidget(self.createToggle("Deformado ON", self.updateMostrarDeformados, True))
        scroll_layout.addWidget(visibility_row)
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
        row.spin_box = spin_box

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
        row.spin_box = spin_box

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

    def createIntegerSpinBox(self, text, min_value, max_value, value, function):
        row = QWidget()
        layout = QVBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel(text))
        spin = QSpinBox()
        spin.setRange(min_value, max(min_value, max_value))
        spin.setValue(value)
        self.styleSpinBox(spin)
        spin.valueChanged.connect(function)
        row.spin_box = spin
        layout.addWidget(spin)
        return row

    def createLabeledIntegerInput(self, text, min_value, max_value, value, function):
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        label = QLabel(text)
        label.setMinimumWidth(145)
        spin = QSpinBox()
        spin.setRange(min_value, max_value)
        spin.setValue(value)
        spin.setFixedWidth(90)
        self.styleSpinBox(spin)
        spin.valueChanged.connect(function)
        row.spin_box = spin
        layout.addWidget(label, 1)
        layout.addWidget(spin)
        return row

    def createPreciseFloatInput(self, text, min_value, max_value, value, function, decimals):
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(text)
        label.setMinimumWidth(145)
        spin = QDoubleSpinBox()
        spin.setDecimals(decimals)
        spin.setRange(min_value, max_value)
        spin.setSingleStep(10 ** -decimals)
        spin.setValue(value)
        spin.setFixedWidth(110)
        self.styleSpinBox(spin)
        spin.valueChanged.connect(function)
        row.spin_box = spin
        layout.addWidget(label, 1)
        layout.addWidget(spin)
        return row

    def styleSpinBox(self, spin):
        spin.setStyleSheet("""
            QSpinBox, QDoubleSpinBox {
                background-color: #111827;
                color: white;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 5px 22px 5px 8px;
            }
            QSpinBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #3B82F6;
                background-color: #0F172A;
            }
            QSpinBox::up-button, QSpinBox::down-button,
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                background-color: #1E293B;
                border: none;
                width: 18px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover,
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #3B82F6;
            }
        """)

    def createToggle(self, text, function, checked):
        button = QPushButton(text)
        button.setCheckable(True)
        button.setChecked(checked)
        button.setMinimumHeight(30)
        button.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: white;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: #3B82F6;
                border-color: #60A5FA;
            }
            QPushButton:hover { border-color: #3B82F6; }
        """)
        button.toggled.connect(function)
        return button







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
        self.dx = value
        self.vara_e_x = min(self.vara_e_x, self.dx - 1)
        self.vara_x_spin.spin_box.setMaximum(self.dx - 1)
        self.vara_x_spin.spin_box.setValue(self.vara_e_x)
        if self.fix_size.isChecked():
            self.updateMalha(self.dx, self.dy, self.dz)
        else:
            self.updateMalha(self.sx, self.sy, self.sz)
        self.updateViewr()

    def updateDy(self, value):
        self.dy = value
        self.vara_e_y = min(self.vara_e_y, self.dy - 1)
        self.vara_y_spin.spin_box.setMaximum(self.dy - 1)
        self.vara_y_spin.spin_box.setValue(self.vara_e_y)
        if self.fix_size.isChecked():
            self.updateMalha(self.dx, self.dy, self.dz)
        else:
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
        self.comprimento_input.spin_box.setMaximum(self.sz)
        if self.comprimento_vara > self.sz:
            self.comprimento_input.spin_box.setValue(self.sz)
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

    def updateVara_e_x(self, value):
        self.vara_e_x = value
        self.updateAll()
    def updateVara_e_y(self, value):
        self.vara_e_y= value
        self.updateAll()

    def updateVaraAtiva(self, checked):
        self.vara_ativa = checked
        self.vara_toggle.setText("ON" if checked else "OFF")
        self.vara_config.setVisible(checked)
        self.updateMalha(self.sx, self.sy, self.sz)
        self.updateViewr()

    def updateRaio(self, value):
        self.raio_vara = value
        self.updateAll()

    def updateComprimento(self, value):
        self.comprimento_vara = min(value, self.sz)
        self.updateAll()

    def updateCamadas(self, value):
        self.camadas_deformadas = value
        self.updateAll()

    def updateMaxDiv(self, value):
        self.max_div = value
        self.min_div_input.spin_box.setMaximum(self.max_div)
        self.updateAll()

    def updateMinDiv(self, value):
        self.min_div = value
        self.max_div_input.spin_box.setMinimum(self.min_div)
        self.updateAll()

    def updateBallooning(self, value):
        self.ballooning = value
        self.updateAll()

    def updateMostrarNormais(self, checked):
        self.mostrar_normais = checked
        self.sender().setText("Normais ON" if checked else "Normais OFF")
        self.updateViewr()

    def updateMostrarDeformados(self, checked):
        self.mostrar_deformados = checked
        self.sender().setText("Deformado ON" if checked else "Deformado OFF")
        self.updateViewr()

    def tetraedrosDosCubos(self, cubos):
        cubos_anteriores = self.malha.final_cube_list
        self.malha.final_cube_list = numpy.asarray(cubos, dtype=int)
        try:
            return self.malha.divCubesInTetraedros()
        finally:
            self.malha.final_cube_list = cubos_anteriores

    def updateViewr(self):
        self.plotter.clear()
        if self.vara_ativa:
            if (
                    self.mostrar_normais
                    and self.cubos_normais is not None
                    and len(self.cubos_normais) > 0
            ):
                Viewer.tetrahedron(self.plotter, self.tetraedrosDosCubos(self.cubos_normais), self.malha.getPointsList(), "Blue", opacity=self.opacity)
            if (
                    self.mostrar_deformados
                    and self.cubos_deformados is not None
                    and len(self.cubos_deformados) > 0
            ):
                Viewer.tetrahedron(self.plotter, self.tetraedrosDosCubos(self.cubos_deformados), self.malha.getPointsList(), "Red", opacity=self.opacity)
        elif self.mostrar_normais:
            Viewer.tetrahedron(self.plotter, self.malha.getTetraedrosList(), self.malha.getPointsList(),"Blue",opacity=self.opacity)

        self.plotter.render()
    def export(self):
        vara_b_ativa = getattr(self, "vara_b_ativa", False)

        if self.vara_ativa or vara_b_ativa:
            vetor = self.malha.gerarVetordaVara(self.malha.getPointsList())
        else:
            vetor = self.malha.getVetorList()

        tetraedros = self.malha.getTetraedrosList()
        pontos = self.malha.getPointsList()
        exp=ex(tetraedros, pontos, vetor, v=1000000)

        if self.vara_ativa and vara_b_ativa:
            tipo_malha = "2Varas"
        elif self.vara_ativa or vara_b_ativa:
            tipo_malha = "1Vara"
        else:
            tipo_malha = "Normal"

        data_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        dados = f"Div({self.dx},{self.dy},{self.dz})-Size({self.sx},{self.sy},{self.sz})-{tipo_malha}-{data_hora}"
        name_e = f"elementos-{dados}"
        name_p = f"pontos-{dados}"
        name_v = f"vetor-{dados}"
        exp.exportAll(name_e,name_p,name_v)

        detalhes_varas = ""
        if self.vara_ativa and vara_b_ativa:
            detalhes_varas = (
                "\nVara 1:\n"
                f"  Posição: ({self.vara_e_x}, {self.vara_e_y})\n"
                f"  Raio: {self.raio_vara}\n"
                f"  Comprimento: {self.comprimento_vara}\n"
                f"  Camadas: {self.camadas_deformadas}\n"
                f"  Divisões mín./máx.: {self.min_div}/{self.max_div}\n"
                f"  Ballooning: {self.ballooning}\n"
                "Vara 2:\n"
                f"  Posição: ({self.vara_b_x}, {self.vara_b_y})\n"
                f"  Raio: {self.raio_vara_b}\n"
                f"  Comprimento: {self.comprimento_vara_b}\n"
                f"  Camadas: {self.camadas_b}\n"
                f"  Divisões mín./máx.: {self.min_div_b}/{self.max_div_b}\n"
                f"  Ballooning: {self.ballooning_b}\n"
            )

            if self.vara_e_x == self.vara_b_x and self.vara_e_y == self.vara_b_y:
                raio_medio = (self.raio_vara + self.raio_vara_b) / 2
                comprimento_medio = (self.comprimento_vara + self.comprimento_vara_b) / 2
                camadas_medias = round((self.camadas_deformadas + self.camadas_b) / 2)
                min_div_medio = round((self.min_div + self.min_div_b) / 2)
                max_div_medio = round((self.max_div + self.max_div_b) / 2)
                ballooning_medio = (self.ballooning + self.ballooning_b) / 2
                detalhes_varas += (
                    "Varas sobrepostas - valores usados:\n"
                    f"  Raio médio: {raio_medio}\n"
                    f"  Comprimento médio: {comprimento_medio}\n"
                    f"  Camadas médias: {camadas_medias}\n"
                    f"  Divisões mín./máx. médias: {min_div_medio}/{max_div_medio}\n"
                    f"  Ballooning médio: {ballooning_medio}\n"
                )
        elif self.vara_ativa:
            detalhes_varas = (
                "\nVara 1:\n"
                f"  Posição: ({self.vara_e_x}, {self.vara_e_y})\n"
                f"  Raio: {self.raio_vara}\n"
                f"  Comprimento: {self.comprimento_vara}\n"
                f"  Camadas: {self.camadas_deformadas}\n"
                f"  Divisões mín./máx.: {self.min_div}/{self.max_div}\n"
                f"  Ballooning: {self.ballooning}\n"
            )
        elif vara_b_ativa:
            detalhes_varas = (
                "\nVara 2:\n"
                f"  Posição: ({self.vara_b_x}, {self.vara_b_y})\n"
                f"  Raio: {self.raio_vara_b}\n"
                f"  Comprimento: {self.comprimento_vara_b}\n"
                f"  Camadas: {self.camadas_b}\n"
                f"  Divisões mín./máx.: {self.min_div_b}/{self.max_div_b}\n"
                f"  Ballooning: {self.ballooning_b}\n"
            )

        mensagem = (
            "Ficheiros exportados com sucesso!\n\n"
            f"Tipo de malha: {tipo_malha}\n"
            f"Data e hora: {data_hora}\n"
            f"Divisões: ({self.dx}, {self.dy}, {self.dz})\n"
            f"Tamanho: ({self.sx}, {self.sy}, {self.sz})\n"
            f"Pontos: {len(pontos)}\n"
            f"Tetraedros: {len(tetraedros)}\n"
            f"Vetor: {vetor.tolist()}\n"
            f"{detalhes_varas}\n"
            "Ficheiros:\n"
            f"{name_e}.txt\n{name_p}.txt\n{name_v}.txt"
        )
        QMessageBox.information(self, "Exportação concluída", mensagem)


    def updateViewXY(self):
        Viewer.viewXY(self.plotter)





    def updateViewXZ(self):
        Viewer.viewXZ(self.plotter)

    def updateViewYZ(self):
        Viewer.viewYZ(self.plotter)
    def updateView3D(self):
        Viewer.view3D(self.plotter)
