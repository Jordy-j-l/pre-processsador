import numpy as np
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QSlider,
    QFrame,
    QScrollArea,
    QMessageBox,
    QLineEdit,
)

from pyvistaqt import QtInteractor

from mesh.Builder import Malha
from visualization.viewer import Viewer
from output.export import Export as ex


class Page1Vara(QWidget):

    def __init__(self, voltar):
        super().__init__()

        self.voltar = voltar

        # Malha
        self.dx = 1
        self.dy = 1
        self.dz = 1

        self.sx = 1
        self.sy = 1
        self.sz = 1

        # Vara
        self.vara_ativa = False
        self.vara_construida = False

        self.vara_e_x = 0
        self.vara_e_y = 0

        self.raio_vara = 0.00794
        self.comprimento_vara = 1.0

        self.estratos = []
        self.resistividades_estratos = []
        self.resistividade_spinboxes = []
        self.dist_fronteira = 0.0

        # Guarda os valores usados no último BUILD
        self.parametros_vara_construida = None

        # Visualização
        self.opacity = 0.6

        self.mostrar_normais = True
        self.mostrar_deformados = True

        self.cubos_normais = None
        self.cubos_deformados = None

        self.setup()

        self.gerarMalhaNormal()


    # ==========================================================
    # MALHA
    # ==========================================================

    def obterTamanhosDaMalha(self):

        if self.fix_size.isChecked():
            tamanho_x = self.dx
            tamanho_y = self.dy
            tamanho_z = self.dz

        else:
            tamanho_x = self.sx
            tamanho_y = self.sy
            tamanho_z = self.sz

        return tamanho_x, tamanho_y, tamanho_z


    def criarObjetoMalha(self):

        tamanho_x, tamanho_y, tamanho_z = self.obterTamanhosDaMalha()

        self.ajustarParametrosDaVara(
            tamanho_x,
            tamanho_y,
            tamanho_z,
        )

        self.malha = Malha(
            self.dx,
            self.dy,
            self.dz,
            tamanho_x,
            tamanho_y,
            tamanho_z,
        )


    def gerarMalhaNormal(self):

        self.criarObjetoMalha()

        pontos, cubos = self.malha.gerarMalhaNormal()

        self.cubos_normais = cubos
        self.cubos_deformados = None

        self.vara_construida = False
        self.parametros_vara_construida = None

        self.updateViewer()


    def buildVara(self):

        if not self.vara_ativa:
            return

        estratos = self.lerEstratos()

        if estratos is None:
            return

        self.estratos = estratos
        self.resistividades_estratos = (
            self.obterResistividadesEstratos()
        )
        self.criarObjetoMalha()

        try:

            pontos, cubos, normais, deformados = (
                self.malha.gerarMalha1Vara(
                    self.vara_e_x,
                    self.vara_e_y,
                    self.raio_vara,
                    self.comprimento_vara,
                    automatico=True,
                    estrato=self.estratos,
                    distVara=self.dist_fronteira,
                )
            )

        except Exception as erro:

            QMessageBox.critical(
                self,
                "Erro ao construir malha",
                str(erro),
            )

            return

        self.cubos_normais = normais
        self.cubos_deformados = deformados

        self.vara_construida = True

        self.parametros_vara_construida = {
            "x": self.vara_e_x,
            "y": self.vara_e_y,
            "raio": self.raio_vara,
            "comprimento": self.comprimento_vara,
            "estratos": self.estratos.copy(),
            "dist_fronteira": self.dist_fronteira,
        }

        self.updateViewer()


    # ==========================================================
    # INTERFACE
    # ==========================================================

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
            interactive=True,
        )

        self.plotter.setStyleSheet(
            "background-color: #2B2B2B;"
        )

        main_layout.addWidget(control_panel, 1)
        main_layout.addWidget(self.plotter, 2)


    def createControlPanel(self):

        panel = QFrame()
        panel.setObjectName("controlPanel")

        panel_layout = QVBoxLayout(panel)

        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        scroll_content.setObjectName("controlPanel")

        scroll_layout = QVBoxLayout(scroll_content)

        scroll_layout.setAlignment(Qt.AlignTop)
        scroll_layout.setSpacing(12)
        scroll_layout.setContentsMargins(25, 25, 25, 25)

        scroll_area.setWidget(scroll_content)

        footer = QWidget()
        footer.setObjectName("controlPanel")

        footer_layout = QVBoxLayout(footer)

        footer_layout.setContentsMargins(20, 20, 20, 20)
        footer_layout.setSpacing(12)

        panel_layout.addWidget(scroll_area)
        panel_layout.addWidget(footer)

        # ======================================================
        # TÍTULO
        # ======================================================

        title = QLabel("Malha com uma Vara")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("panelTitle")

        scroll_layout.addWidget(title)
        scroll_layout.addSpacing(20)

        # ======================================================
        # DIVISÕES
        # ======================================================

        section_mesh = QLabel("Divisões da Malha")
        section_mesh.setObjectName("sectionTitle")

        scroll_layout.addWidget(section_mesh)

        div_x_widget = self.createInputInt(
            "Div-x",
            1,
            20,
            self.dx,
            self.updateDx,
        )

        div_y_widget = self.createInputInt(
            "Div-y",
            1,
            20,
            self.dy,
            self.updateDy,
        )

        div_z_widget = self.createInputInt(
            "Div-z",
            1,
            20,
            self.dz,
            self.updateDz,
        )

        scroll_layout.addWidget(div_x_widget)
        scroll_layout.addWidget(div_y_widget)
        scroll_layout.addWidget(div_z_widget)

        scroll_layout.addSpacing(20)

        # ======================================================
        # TAMANHO FÍSICO
        # ======================================================

        section_size = QLabel("Dimensões Físicas")
        section_size.setObjectName("sectionTitle")

        wsx = self.createInputFloat(
            "Size-x",
            0.1,
            50,
            self.sx,
            self.updateSx,
        )

        wsy = self.createInputFloat(
            "Size-y",
            0.1,
            50,
            self.sy,
            self.updateSy,
        )

        wsz = self.createInputFloat(
            "Size-z",
            0.1,
            50,
            self.sz,
            self.updateSz,
        )

        size_header = QWidget()

        size_header_layout = QHBoxLayout(size_header)

        size_header_layout.setContentsMargins(0, 0, 0, 0)

        size_header_layout.addWidget(section_size)

        self.fix_size = QCheckBox("SYNC")
        self.fix_size.setChecked(False)

        self.fix_size.toggled.connect(
            lambda checked: self.updateFixSize(
                checked,
                wsx,
                wsy,
                wsz,
            )
        )

        size_header_layout.addWidget(self.fix_size)

        scroll_layout.addWidget(size_header)

        scroll_layout.addWidget(wsx)
        scroll_layout.addWidget(wsy)
        scroll_layout.addWidget(wsz)

        scroll_layout.addSpacing(15)

        # ======================================================
        # VARA
        # ======================================================

        vara_setup = QLabel("Setup Vara")
        vara_setup.setObjectName("sectionTitle")

        setup_row = QWidget()

        setup_layout = QHBoxLayout(setup_row)
        setup_layout.setContentsMargins(0, 0, 0, 0)

        setup_layout.addWidget(vara_setup)

        self.vara_toggle = QCheckBox("OFF")
        self.vara_toggle.setChecked(False)

        self.vara_toggle.toggled.connect(
            self.updateVaraAtiva
        )

        setup_layout.addWidget(self.vara_toggle)

        scroll_layout.addWidget(setup_row)

        # ======================================================
        # CONFIGURAÇÃO DA VARA
        # ======================================================

        self.vara_config = QWidget()

        vara_config_layout = QVBoxLayout(
            self.vara_config
        )

        vara_config_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        vara_config_layout.setSpacing(10)

        # Posição
        vara_config_layout.addWidget(
            QLabel("Posição da Vara")
        )

        self.vara_x_spin = self.createLabeledIntegerInput(
            "Eixo X",
            0,
            self.dx - 1,
            self.vara_e_x,
            self.updateVaraX,
        )

        self.vara_y_spin = self.createLabeledIntegerInput(
            "Eixo Y",
            0,
            self.dy - 1,
            self.vara_e_y,
            self.updateVaraY,
        )

        vara_config_layout.addWidget(
            self.vara_x_spin
        )

        vara_config_layout.addWidget(
            self.vara_y_spin
        )

        # Comprimento
        self.comprimento_input = (
            self.createPreciseFloatInput(
                "Comprimento",
                0.1,
                self.sz,
                self.comprimento_vara,
                self.updateComprimento,
                2,
            )
        )

        vara_config_layout.addWidget(
            self.comprimento_input
        )

        # Raio
        self.raio_input = (
            self.createPreciseFloatInput(
                "Raio",
                0.00001,
                self._raioMaximo(
                    self.sx,
                    self.sy,
                ),
                self.raio_vara,
                self.updateRaio,
                5,
            )
        )

        vara_config_layout.addWidget(
            self.raio_input
        )



        # BUILD
        build_button = self.createBuildButton()

        vara_config_layout.addSpacing(5)
        vara_config_layout.addWidget(build_button)

        self.vara_config.setVisible(False)

        scroll_layout.addWidget(
            self.vara_config
        )
        scroll_layout.addSpacing(15)

        # ======================================================
        # SOLO
        # ======================================================

        solo_setup = QLabel("Setup Solo")
        solo_setup.setObjectName("sectionTitle")

        scroll_layout.addWidget(
            solo_setup
        )

        # Estratos
        self.estratos_input = self.createTextInput(
            "Estratos",
            "Ex.: 1, 2.5, 4",
        )

        scroll_layout.addWidget(
            self.estratos_input
        )

        # Resistividades dos estratos
        self.resistividades_container = QWidget()

        self.resistividades_layout = QVBoxLayout(
            self.resistividades_container
        )

        self.resistividades_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.resistividades_layout.setSpacing(10)

        scroll_layout.addWidget(
            self.resistividades_container
        )

        self.estratos_input.line_edit.textChanged.connect(
            self.atualizarResistividadesEstratos
        )

        # Distância da vara à fronteira
        self.dist_fronteira_input = (
            self.createPreciseFloatInput(
                "Dist. fronteira",
                0.0,
                100000.0,
                self.dist_fronteira,
                self.updateDistFronteira,
                3,
            )
        )

        scroll_layout.addWidget(
            self.dist_fronteira_input
        )
        scroll_layout.addSpacing(15)

        # ======================================================
        # VISUALIZAÇÃO DA MALHA
        # ======================================================

        view_mesh = QLabel("View Malha")
        view_mesh.setObjectName("sectionTitle")

        scroll_layout.addWidget(view_mesh)

        visibility_row = QWidget()

        visibility_layout = QHBoxLayout(
            visibility_row
        )

        visibility_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        visibility_layout.addWidget(
            self.createToggle(
                "Normais ON",
                self.updateMostrarNormais,
                True,
            )
        )

        visibility_layout.addWidget(
            self.createToggle(
                "Deformado ON",
                self.updateMostrarDeformados,
                True,
            )
        )

        scroll_layout.addWidget(
            visibility_row
        )

        # ======================================================
        # VISTA
        # ======================================================

        view_setup = QLabel("View Setup")
        view_setup.setObjectName("sectionTitle")

        scroll_layout.addWidget(view_setup)

        scroll_layout.addWidget(
            self.createSpinBox(
                "Opacidade",
                0.1,
                1.0,
                self.opacity,
                self.updateOpacity,
            )
        )

        row2 = QWidget()
        row2_layout = QHBoxLayout(row2)

        row2_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        row2_layout.addWidget(
            self.createButtonClean(
                "View YX",
                self.updateViewXY,
            )
        )

        row2_layout.addWidget(
            self.createButtonClean(
                "View ZX",
                self.updateViewXZ,
            )
        )

        scroll_layout.addWidget(row2)

        row3 = QWidget()
        row3_layout = QHBoxLayout(row3)

        row3_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        row3_layout.addWidget(
            self.createButtonClean(
                "View ZY",
                self.updateViewYZ,
            )
        )

        row3_layout.addWidget(
            self.createButtonClean(
                "View 3D",
                self.updateView3D,
            )
        )

        scroll_layout.addWidget(row3)

        # ======================================================
        # FOOTER
        # ======================================================

        footer_row = QWidget()

        footer_row_layout = QHBoxLayout(
            footer_row
        )

        footer_row_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        voltar_button = self.createButton(
            "Voltar",
            self.voltar,
        )

        export_button = self.createButton(
            "Exportar",
            self.export,
        )

        footer_row_layout.addWidget(
            voltar_button
        )

        footer_row_layout.addWidget(
            export_button
        )

        footer_layout.addWidget(
            footer_row
        )

        # ======================================================
        # ESTILO
        # ======================================================

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


    # ==========================================================
    # COMPONENTES
    # ==========================================================

    def createButton(self, text, function):

        button = QPushButton(text)

        button.setFixedSize(140, 50)

        button.clicked.connect(function)

        button.setStyleSheet("""
            QPushButton {
                background-color: rgba(70, 144, 218, 230);
                color: black;
                font-size: 15px;
                border-radius: 8px;
                padding: 6px;
            }

            QPushButton:hover {
                background-color: rgba(245, 245, 245, 120);
            }
        """)

        return button


    def createBuildButton(self):

        button = QPushButton("BUILD")

        button.setMinimumHeight(42)

        button.clicked.connect(
            self.buildVara
        )

        button.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                font-size: 15px;
                font-weight: bold;
                border: 1px solid #60A5FA;
                border-radius: 7px;
                padding: 8px;
            }

            QPushButton:hover {
                background-color: #2563EB;
            }

            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)

        return button


    def createButtonClean(self, text, function):

        button = QPushButton(
            f"[ {text} ]"
        )

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


    def createInputInt(
        self,
        text,
        min_value,
        max_value,
        value,
        function,
    ):

        row = QWidget()

        row_layout = QHBoxLayout(row)

        row_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        label = QLabel(text)
        label.setFixedWidth(40)

        slider = QSlider(Qt.Horizontal)

        slider.setRange(
            min_value,
            max_value,
        )

        slider.setValue(value)

        spin_box = QSpinBox()

        spin_box.setRange(
            min_value,
            max_value,
        )

        spin_box.setValue(value)
        spin_box.setFixedWidth(80)

        slider.valueChanged.connect(
            spin_box.setValue
        )

        spin_box.valueChanged.connect(
            slider.setValue
        )

        spin_box.valueChanged.connect(
            function
        )

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

        self.styleSpinBox(spin_box)

        row_layout.addWidget(label)
        row_layout.addWidget(slider)
        row_layout.addWidget(spin_box)

        row.spin_box = spin_box

        return row


    def createInputFloat(
        self,
        text,
        min_value,
        max_value,
        value,
        function,
    ):

        row = QWidget()

        row_layout = QHBoxLayout(row)

        row_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        label = QLabel(text)
        label.setFixedWidth(40)

        slider = QSlider(Qt.Horizontal)

        slider.setMinimum(
            int(min_value)
        )

        slider.setMaximum(
            int(max_value)
        )

        slider.setValue(
            int(value)
        )

        spin_box = QDoubleSpinBox()

        spin_box.setRange(
            min_value,
            max_value,
        )

        spin_box.setDecimals(1)
        spin_box.setSingleStep(0.1)

        spin_box.setValue(value)
        spin_box.setFixedWidth(80)

        slider.valueChanged.connect(
            spin_box.setValue
        )

        spin_box.valueChanged.connect(
            slider.setValue
        )

        spin_box.valueChanged.connect(
            function
        )

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

        self.styleSpinBox(spin_box)

        row_layout.addWidget(label)
        row_layout.addWidget(slider)
        row_layout.addWidget(spin_box)

        row.spin_box = spin_box

        return row


    def createSpinBox(
        self,
        text,
        min_value,
        max_value,
        value,
        function,
    ):

        row = QWidget()

        row_layout = QHBoxLayout(row)

        row_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        label = QLabel(text)

        spin_box = QDoubleSpinBox()

        spin_box.setRange(
            min_value,
            max_value,
        )

        spin_box.setDecimals(1)
        spin_box.setSingleStep(0.1)

        spin_box.setValue(value)
        spin_box.setFixedWidth(80)

        spin_box.valueChanged.connect(
            function
        )

        self.styleSpinBox(spin_box)

        row_layout.addWidget(label)
        row_layout.addWidget(spin_box)

        return row


    def createLabeledIntegerInput(
        self,
        text,
        min_value,
        max_value,
        value,
        function,
    ):

        row = QWidget()

        layout = QHBoxLayout(row)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        label = QLabel(text)

        label.setMinimumWidth(145)

        spin = QSpinBox()

        spin.setRange(
            min_value,
            max_value,
        )

        spin.setValue(value)

        spin.setFixedWidth(90)

        self.styleSpinBox(spin)

        spin.valueChanged.connect(
            function
        )

        layout.addWidget(label, 1)
        layout.addWidget(spin)

        row.spin_box = spin

        return row


    def createPreciseFloatInput(
        self,
        text,
        min_value,
        max_value,
        value,
        function,
        decimals,
    ):

        row = QWidget()

        layout = QHBoxLayout(row)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        label = QLabel(text)

        label.setMinimumWidth(145)

        spin = QDoubleSpinBox()

        spin.setDecimals(decimals)

        spin.setRange(
            min_value,
            max_value,
        )

        spin.setSingleStep(
            10 ** -decimals
        )

        spin.setValue(value)

        spin.setFixedWidth(110)

        self.styleSpinBox(spin)

        spin.valueChanged.connect(
            function
        )

        layout.addWidget(label, 1)
        layout.addWidget(spin)

        row.spin_box = spin

        return row


    def createTextInput(
        self,
        text,
        placeholder,
    ):

        row = QWidget()

        layout = QHBoxLayout(row)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        label = QLabel(text)

        label.setMinimumWidth(145)

        line_edit = QLineEdit()

        line_edit.setPlaceholderText(
            placeholder
        )

        line_edit.setStyleSheet("""
            QLineEdit {
                background-color: #111827;
                color: white;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px;
            }

            QLineEdit:focus {
                border: 2px solid #3B82F6;
                background-color: #0F172A;
            }
        """)

        layout.addWidget(label, 1)
        layout.addWidget(line_edit)

        row.line_edit = line_edit

        return row


    def styleSpinBox(self, spin):

        spin.setStyleSheet("""
            QSpinBox,
            QDoubleSpinBox {
                background-color: #111827;
                color: white;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 5px 22px 5px 8px;
            }

            QSpinBox:focus,
            QDoubleSpinBox:focus {
                border: 2px solid #3B82F6;
                background-color: #0F172A;
            }

            QSpinBox::up-button,
            QSpinBox::down-button,
            QDoubleSpinBox::up-button,
            QDoubleSpinBox::down-button {
                background-color: #1E293B;
                border: none;
                width: 18px;
            }

            QSpinBox::up-button:hover,
            QSpinBox::down-button:hover,
            QDoubleSpinBox::up-button:hover,
            QDoubleSpinBox::down-button:hover {
                background-color: #3B82F6;
            }
        """)


    def createToggle(
        self,
        text,
        function,
        checked,
    ):

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

            QPushButton:hover {
                border-color: #3B82F6;
            }
        """)

        button.toggled.connect(
            function
        )

        return button


    # ==========================================================
    # ESTRATOS
    # ==========================================================

    def lerEstratos(self):

        texto = self.estratos_input.line_edit.text()

        texto = texto.strip()

        if texto == "":
            return []

        texto = texto.replace(
            "[",
            "",
        )

        texto = texto.replace(
            "]",
            "",
        )

        texto = texto.replace(
            ";",
            ",",
        )

        partes = texto.split(",")

        estratos = []

        for parte in partes:

            parte = parte.strip()

            if parte == "":
                continue

            try:
                valor = float(parte)

            except ValueError:

                QMessageBox.warning(
                    self,
                    "Estratos inválidos",
                    "Utiliza valores numéricos separados por vírgulas.\n"
                    "Exemplo: 1, 2.5, 4",
                )

                return None

            estratos.append(valor)

        return estratos


    # ==========================================================
    # LIMITES DA VARA
    # ==========================================================

    def _raioMaximo(
        self,
        tamanho_x,
        tamanho_y,
    ):

        tamanho_cubo_x = (
            tamanho_x / self.dx
        )

        tamanho_cubo_y = (
            tamanho_y / self.dy
        )

        tamanho_cubo = min(
            tamanho_cubo_x,
            tamanho_cubo_y,
        )

        raio_maximo = (
            tamanho_cubo / 2
        ) - 0.00001

        return max(
            0.00001,
            raio_maximo,
        )


    def ajustarParametrosDaVara(
        self,
        tamanho_x,
        tamanho_y,
        tamanho_z,
    ):

        raio_maximo = self._raioMaximo(
            tamanho_x,
            tamanho_y,
        )

        if self.raio_vara > raio_maximo:
            self.raio_vara = raio_maximo

        self.raio_input.spin_box.blockSignals(True)

        self.raio_input.spin_box.setMaximum(
            raio_maximo
        )

        self.raio_input.spin_box.setValue(
            self.raio_vara
        )

        self.raio_input.spin_box.blockSignals(False)

        if self.comprimento_vara > tamanho_z:
            self.comprimento_vara = tamanho_z

        self.comprimento_input.spin_box.blockSignals(
            True
        )

        self.comprimento_input.spin_box.setMaximum(
            tamanho_z
        )

        self.comprimento_input.spin_box.setValue(
            self.comprimento_vara
        )

        self.comprimento_input.spin_box.blockSignals(
            False
        )


    # ==========================================================
    # ALTERAÇÕES DA MALHA NORMAL
    # ==========================================================

    def updateFixSize(
        self,
        checked,
        widget1,
        widget2,
        widget3,
    ):

        if checked:

            widget1.setVisible(False)
            widget2.setVisible(False)
            widget3.setVisible(False)

        else:

            widget1.setVisible(True)
            widget2.setVisible(True)
            widget3.setVisible(True)

        self.gerarMalhaNormal()


    def updateDx(self, value):

        self.dx = value

        if self.vara_e_x >= self.dx:
            self.vara_e_x = self.dx - 1

        self.vara_x_spin.spin_box.setMaximum(
            self.dx - 1
        )

        self.vara_x_spin.spin_box.setValue(
            self.vara_e_x
        )

        self.gerarMalhaNormal()


    def updateDy(self, value):

        self.dy = value

        if self.vara_e_y >= self.dy:
            self.vara_e_y = self.dy - 1

        self.vara_y_spin.spin_box.setMaximum(
            self.dy - 1
        )

        self.vara_y_spin.spin_box.setValue(
            self.vara_e_y
        )

        self.gerarMalhaNormal()


    def updateDz(self, value):

        self.dz = value

        self.gerarMalhaNormal()


    def updateSx(self, value):

        self.sx = value

        self.gerarMalhaNormal()


    def updateSy(self, value):

        self.sy = value

        self.gerarMalhaNormal()


    def updateSz(self, value):

        self.sz = value

        self.gerarMalhaNormal()


    # ==========================================================
    # ALTERAÇÕES DA VARA
    #
    # Estas funções NÃO geram malha.
    # Só alteram os valores.
    # ==========================================================



    def updateVaraAtiva(
        self,
        checked,
    ):

        self.vara_ativa = checked

        if checked:
            self.vara_toggle.setText("ON")

        else:
            self.vara_toggle.setText("OFF")

        self.vara_config.setVisible(
            checked
        )

        self.gerarMalhaNormal()


    def updateVaraX(
        self,
        value,
    ):

        self.vara_e_x = value


    def updateVaraY(
        self,
        value,
    ):

        self.vara_e_y = value


    def updateRaio(
        self,
        value,
    ):

        self.raio_vara = value


    def updateComprimento(
        self,
        value,
    ):

        self.comprimento_vara = value


    def updateDistFronteira(
        self,
        value,
    ):

        self.dist_fronteira = value


    # ==========================================================
    # VISUALIZAÇÃO
    # ==========================================================

    def updateOpacity(
        self,
        value,
    ):

        self.opacity = value

        self.updateViewer()


    def updateMostrarNormais(
        self,
        checked,
    ):

        self.mostrar_normais = checked

        if checked:
            self.sender().setText(
                "Normais ON"
            )

        else:
            self.sender().setText(
                "Normais OFF"
            )

        self.updateViewer()


    def updateMostrarDeformados(
        self,
        checked,
    ):

        self.mostrar_deformados = checked

        if checked:
            self.sender().setText(
                "Deformado ON"
            )

        else:
            self.sender().setText(
                "Deformado OFF"
            )

        self.updateViewer()


    def tetraedrosDosCubos(
        self,
        cubos,
    ):

        cubos = np.asarray(
            cubos,
            dtype=int,
        )

        pontos = self.malha.getPointsList()

        tetraedros = (
            self.malha.divCubesInTetraedrosF(
                cubos,
                pontos,
            )
        )

        return tetraedros


    def updateViewer(self):

        self.plotter.clear()

        # Malha com vara já construída
        if self.vara_construida:

            if (
                self.mostrar_normais
                and self.cubos_normais is not None
                and len(self.cubos_normais) > 0
            ):

                tetraedros_normais = (
                    self.tetraedrosDosCubos(
                        self.cubos_normais
                    )
                )

                Viewer.tetrahedron(
                    self.plotter,
                    tetraedros_normais,
                    self.malha.getPointsList(),
                    "Blue",
                    opacity=self.opacity,
                )

            if (
                self.mostrar_deformados
                and self.cubos_deformados is not None
                and len(self.cubos_deformados) > 0
            ):

                tetraedros_deformados = (
                    self.tetraedrosDosCubos(
                        self.cubos_deformados
                    )
                )

                Viewer.tetrahedron(
                    self.plotter,
                    tetraedros_deformados,
                    self.malha.getPointsList(),
                    "Red",
                    opacity=self.opacity,
                )

        # Malha normal
        else:

            if self.mostrar_normais:

                Viewer.tetrahedron(
                    self.plotter,
                    self.malha.getTetraedrosList(),
                    self.malha.getPointsList(),
                    "Blue",
                    opacity=self.opacity,
                )

        self.plotter.render()


    # ==========================================================
    # EXPORTAÇÃO
    # ==========================================================
    def atualizarResistividadesEstratos(self):

        estratos = self.lerEstratosSemMensagem()

        if estratos is None:
            return

        valores_antigos = []

        for spin_box in self.resistividade_spinboxes:
            valores_antigos.append(
                spin_box.value()
            )

        self.limparResistividadesEstratos()

        for i in range(len(estratos)):

            valor_inicial = 1.0

            if i < len(valores_antigos):
                valor_inicial = valores_antigos[i]

            widget = self.criarInputResistividadeEstrato(
                i + 1,
                valor_inicial,
            )

            self.resistividades_layout.addWidget(
                widget
            )

    def limparResistividadesEstratos(self):

        while self.resistividades_layout.count() > 0:

            item = self.resistividades_layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        self.resistividade_spinboxes = []

    def criarInputResistividadeEstrato(
            self,
            numero_estrato,
            valor,
    ):

        row = QWidget()

        layout = QHBoxLayout(row)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        label = QLabel(
            f"Estrato {numero_estrato} (ρ - Ω·m)"
        )

        label.setMinimumWidth(145)

        spin_box = QDoubleSpinBox()

        spin_box.setDecimals(3)

        spin_box.setRange(
            0.001,
            1000000000.0,
        )

        spin_box.setValue(valor)

        spin_box.setSingleStep(1.0)

        spin_box.setFixedWidth(110)

        self.styleSpinBox(
            spin_box
        )

        layout.addWidget(
            label,
            1,
        )

        layout.addWidget(
            spin_box
        )

        self.resistividade_spinboxes.append(
            spin_box
        )

        return row

    def lerEstratosSemMensagem(self):

        texto = self.estratos_input.line_edit.text()

        texto = texto.strip()

        if texto == "":
            return []

        texto = texto.replace(
            "[",
            "",
        )

        texto = texto.replace(
            "]",
            "",
        )

        texto = texto.replace(
            ";",
            ",",
        )

        partes = texto.split(",")

        estratos = []

        for parte in partes:

            parte = parte.strip()

            if parte == "":
                continue

            try:
                valor = float(parte)

            except ValueError:
                return None

            estratos.append(valor)

        return estratos

    def obterResistividadesEstratos(self):

        resistividades = []

        for spin_box in self.resistividade_spinboxes:
            resistividades.append(
                spin_box.value()
            )

        return resistividades

    def export(self):

        tetraedros, pontos = self.malha.clean(
            self.malha.getCubesList(),
            self.malha.getPointsList(),
        )

        if self.vara_construida:

            vetor = self.malha.gerarVetordaVara(
                pontos
            )

            tipo_malha = "1Vara"

        else:

            vetor = self.malha.getVetorList()

            tipo_malha = "Normal"

        altura_malha = self.malha.sz

        minimos = np.min(
            pontos[
                tetraedros[:, 1:5],
                2,
            ],
            axis=1,
        )

        export_tetra = np.empty(
            (
                len(tetraedros),
                5,
            ),
            dtype=int,
        )

        for i in range(
            len(tetraedros)
        ):

            export_tetra[i, 0] = (
                tetraedros[i][1]
            )

            export_tetra[i, 1] = (
                tetraedros[i][2]
            )

            export_tetra[i, 2] = (
                tetraedros[i][3]
            )

            export_tetra[i, 3] = (
                tetraedros[i][4]
            )

            if altura_malha >= 4:

                if (
                    minimos[i]
                    >= altura_malha - 4
                ):

                    export_tetra[i, 4] = 0

                else:

                    export_tetra[i, 4] = 1

            else:

                export_tetra[i, 4] = 0

        exportador = ex(
            export_tetra,
            pontos,
            vetor,
            v=1000000,
        )

        data_hora = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        dados = (
            f"Div({self.malha.dx},{self.malha.dy},{self.malha.dz})"
            f"-Size({self.malha.sx},{self.malha.sy},{self.malha.sz})"
            f"-{tipo_malha}"
            f"-{data_hora}"
        )

        nome_elementos = (
            f"elementos-{dados}"
        )

        nome_pontos = (
            f"pontos-{dados}"
        )

        nome_vetor = (
            f"vetor-{dados}"
        )

        exportador.exportAll(
            nome_elementos,
            nome_pontos,
            nome_vetor,
        )

        detalhes_vara = ""

        if (
            self.vara_construida
            and self.parametros_vara_construida
            is not None
        ):

            parametros = (
                self.parametros_vara_construida
            )

            detalhes_vara = (
                "\nVara:\n"
                f"  Posição: "
                f"({parametros['x']}, {parametros['y']})\n"
                f"  Raio: {parametros['raio']}\n"
                f"  Comprimento: {parametros['comprimento']}\n"
                f"  Estratos: {parametros['estratos']}\n"
                f"  Dist. fronteira: "
                f"{parametros['dist_fronteira']}\n"
            )

        mensagem = (
            "Ficheiros exportados com sucesso!\n\n"
            f"Tipo de malha: {tipo_malha}\n"
            f"Data e hora: {data_hora}\n"
            f"Divisões: "
            f"({self.malha.dx}, "
            f"{self.malha.dy}, "
            f"{self.malha.dz})\n"
            f"Tamanho: "
            f"({self.malha.sx}, "
            f"{self.malha.sy}, "
            f"{self.malha.sz})\n"
            f"Pontos: {len(pontos)}\n"
            f"Tetraedros: {len(tetraedros)}\n"
            f"{detalhes_vara}\n"
            "Ficheiros:\n"
            f"{nome_elementos}.txt\n"
            f"{nome_pontos}.txt\n"
            f"{nome_vetor}.txt"
        )

        QMessageBox.information(
            self,
            "Exportação concluída",
            mensagem,
        )


    # ==========================================================
    # CÂMARA
    # ==========================================================

    def updateViewXY(self):
        Viewer.viewXY(
            self.plotter
        )


    def updateViewXZ(self):
        Viewer.viewXZ(
            self.plotter
        )


    def updateViewYZ(self):
        Viewer.viewYZ(
            self.plotter
        )


    def updateView3D(self):
        Viewer.view3D(
            self.plotter
        )



    # ==========================================================
    # DESNECESSÁRIO
    # ==========================================================

    # import numpy
    # desnecessario

    # self.camadas_deformadas = 6
    # desnecessario

    # self.max_div = 4
    # desnecessario

    # self.min_div = 1
    # desnecessario

    # self.ballooning = 1.55
    # desnecessario

    # def updateCamadas(self, value):
    #     self.camadas_deformadas = value
    # desnecessario

    # def updateMaxDiv(self, value):
    #     self.max_div = value
    # desnecessario

    # def updateMinDiv(self, value):
    #     self.min_div = value
    # desnecessario

    # def updateBallooning(self, value):
    #     self.ballooning = value
    # desnecessario

    # def updateAll(self):
    #     ...
    # desnecessario

    # QApplication
    # QMainWindow
    # QStackedWidget
    # QGridLayout
    # desnecessario