from PySide6.QtCore import Qt
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
    QCheckBox
)

class MenuPrincipal(QWidget):
    def __init__(self,abrir_placas,abrir_1_vara,abrir_2_varas,abrir_malha):
        super().__init__()
        self.abrir_placas = abrir_placas
        self.abrir_1_vara = abrir_1_vara
        self.abrir_2_varas = abrir_2_varas
        self.abrir_malha = abrir_malha
        self.setup()



    def setup(self):
        #BACKGROUND
        self.setObjectName("menuPrincipal")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            #menuPrincipal {
                border-image: url("assets/background.png") 0 0 0 0 stretch stretch;
            }
        """)
        #PAGE LAYOUT CONFIG
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        self.setLayout(layout)
        builder = QLabel("BUILDER")
        builder.setAlignment(Qt.AlignCenter)

        #PAGE ELEMENTS
        visualizacao = QLabel("VISUALIZAÇÃO")
        visualizacao.setAlignment(Qt.AlignCenter)

        builder.setStyleSheet("font-size: 22px; font-weight: bold; color: Black;")
        visualizacao.setStyleSheet("font-size: 22px; font-weight: bold; color: Black;")


        btn_placas = self.createButton("Placas Paralelas", self.abrir_placas)
        btn_1_vara = self.createButton("1 Vara", self.abrir_1_vara)
        btn_2_varas = self.createButton("2 Varas", self.abrir_2_varas)
        btn_malha = self.createButton("Malha", self.abrir_malha)

        #Adiciona os elementos ao layout

        layout.addSpacing(30)

        layout.addWidget(builder)
        layout.addWidget(btn_placas)
        layout.addWidget(btn_1_vara)
        layout.addWidget(btn_2_varas)

        layout.addSpacing(30)

        layout.addWidget(visualizacao)
        layout.addWidget(btn_malha)


    def createButton(self, text, function):
        button = QPushButton(text)
        button.setFixedSize(320, 50)
        button.clicked.connect(function)

        button.setStyleSheet("""
            QPushButton {
                background-color: rgba(162, 158, 158,190);
                color: White;
                font-size: 18px;
                border-radius: 8px;
                padding: 8px;
            }

            QPushButton:hover {
                background-color: rgba(70, 144, 218, 230);
            }
        """)

        return button