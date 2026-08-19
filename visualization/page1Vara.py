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

        self.raio_vara = 0.00794
        self.comprimento_vara = 1.0

        # Configuração avançada
        self.avancado_ativo = False

        self.vara_e_x = 0
        self.vara_e_y = 0

        self.max_div = None
        self.min_div = 1
        self.camadas_deformadas = None
        self.ballooning = 1.55

        self.divisoes_xy = None
        self.divisoes_contorno = None
        self.divisoes_z_vara = None

        self.estratos = []
        self.resistividades_estratos = []
        self.resistividade_spinboxes = []
        self.dist_fronteira = 0.0
        self.potencial=1000000.0
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

        if (
                self.avancado_ativo
                and self.max_div is not None
                and self.max_div < self.min_div
        ):
            QMessageBox.warning(
                self,
                "Configuração inválida",
                "Máx. divisões não pode ser inferior a Mín. divisões.",
            )
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

                    self.max_div,
                    self.min_div,
                    self.camadas_deformadas,
                    self.ballooning,

                    divisoes_xy=self.divisoes_xy,
                    divisoes_contorno=self.divisoes_contorno,
                    divisoes_z_vara=self.divisoes_z_vara,

                    automatico=not self.avancado_ativo,

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

            "avancado": self.avancado_ativo,

            "max_div": self.max_div,
            "min_div": self.min_div,
            "camadas_deformadas": self.camadas_deformadas,
            "ballooning": self.ballooning,

            "divisoes_xy": self.divisoes_xy,
            "divisoes_contorno": self.divisoes_contorno,
            "divisoes_z_vara": self.divisoes_z_vara,

            "estratos": self.estratos.copy(),
            "dist_fronteira": self.dist_fronteira,
        }
        if not self.avancado_ativo:
            self.vara_e_x, self.vara_e_y = (
                self.calcularCuboAutomaticoVara()
            )

            self.avisarVaraNaoCentrada()
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

        self.wsx = self.createInputFloat(
            "Size-x",
            0.1,
            100000,
            self.sx,
            self.updateSx,
        )

        self.wsy = self.createInputFloat(
            "Size-y",
            0.1,
            100000,
            self.sy,
            self.updateSy,
        )

        self.wsz = self.createInputFloat(
            "Size-z",
            0.1,
            100000,
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
                self.wsx,
                self.wsy,
                self.wsz,
            )
        )

        size_header_layout.addWidget(self.fix_size)

        scroll_layout.addWidget(size_header)

        scroll_layout.addWidget(self.wsx)
        scroll_layout.addWidget(self.wsy)
        scroll_layout.addWidget(self.wsz)

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

        # Raio
        self.raio_input = self.createPreciseFloatInput(
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

        vara_config_layout.addWidget(
            self.raio_input
        )

        # Comprimento
        self.comprimento_input = self.createPreciseFloatInput(
            "Comprimento",
            0.1,
            self.sz,
            self.comprimento_vara,
            self.updateComprimento,
            2,
        )

        vara_config_layout.addWidget(
            self.comprimento_input
        )

        # ======================================================
        # AVANÇADO
        # ======================================================

        self.avancado_checkbox = QCheckBox(
            "Avançado"
        )

        self.avancado_checkbox.setChecked(
            False
        )

        self.avancado_checkbox.toggled.connect(
            self.updateAvancado
        )

        vara_config_layout.addWidget(
            self.avancado_checkbox
        )

        self.avancado_container = QWidget()

        avancado_layout = QVBoxLayout(
            self.avancado_container
        )

        avancado_layout.setContentsMargins(
            10,
            5,
            0,
            5,
        )

        avancado_layout.setSpacing(10)

        # Posição X
        self.vara_x_spin = self.createAdvancedIntegerInput(
            "Cubo Vara X",
            0,
            self.dx - 1,
            self.vara_e_x,
            self.updateVaraX,
            (
                "Índice do cubo no eixo X onde a vara será colocada. "
                "O primeiro cubo tem índice 0."
            ),
        )

        avancado_layout.addWidget(
            self.vara_x_spin
        )

        # Posição Y
        self.vara_y_spin = self.createAdvancedIntegerInput(
            "Cubo Vara Y",
            0,
            self.dy - 1,
            self.vara_e_y,
            self.updateVaraY,
            (
                "Índice do cubo no eixo Y onde a vara será colocada. "
                "Em conjunto com Cubo Vara X define o bloco da malha "
                "que será deformado para receber a vara."
            ),
        )

        avancado_layout.addWidget(
            self.vara_y_spin
        )

        # Máximo de divisões
        self.max_div_input = self.createAdvancedIntegerInput(
            "Máx. divisões",
            0,
            100,
            self.max_div,
            self.updateMaxDiv,
            (
                "Define o limite máximo de divisões utilizado na "
                "discretização da região da vara. "
                "Auto deixa o gerador determinar este valor."
            ),
            allow_none=True,
        )

        avancado_layout.addWidget(
            self.max_div_input
        )

        # Mínimo de divisões
        self.min_div_input = self.createAdvancedIntegerInput(
            "Mín. divisões",
            1,
            100,
            self.min_div,
            self.updateMinDiv,
            (
                "Define o número mínimo de divisões permitido durante "
                "a discretização da região deformada da vara."
            ),
        )

        avancado_layout.addWidget(
            self.min_div_input
        )

        # Camadas deformadas
        self.camadas_input = self.createAdvancedIntegerInput(
            "Camadas deformadas",
            0,
            100,
            self.camadas_deformadas,
            self.updateCamadasDeformadas,
            (
                "Número de camadas criadas entre o contorno da vara "
                "e o limite exterior da região deformada. "
                "Auto deixa o gerador determinar este valor."
            ),
            allow_none=True,
        )

        avancado_layout.addWidget(
            self.camadas_input
        )

        # Ballooning
        self.ballooning_input = self.createAdvancedFloatInput(
            "Ballooning",
            1.0,
            10.0,
            self.ballooning,
            self.updateBallooning,
            2,
            (
                "Razão de crescimento entre camadas sucessivas da "
                "região deformada. Valores maiores concentram elementos "
                "mais pequenos junto à vara e aumentam progressivamente "
                "o tamanho dos elementos ao afastar-se dela."
            ),
        )

        avancado_layout.addWidget(
            self.ballooning_input
        )

        # Divisões XY
        self.divisoes_xy_input = self.createAdvancedIntegerInput(
            "Divisões XY",
            0,
            1000,
            self.divisoes_xy,
            self.updateDivisoesXY,
            (
                "Força o número de divisões utilizado no plano XY "
                "da região especial da vara. "
                "Auto deixa o gerador calcular este valor."
            ),
            allow_none=True,
        )

        avancado_layout.addWidget(
            self.divisoes_xy_input
        )

        # Divisões do contorno
        self.divisoes_contorno_input = self.createAdvancedIntegerInput(
            "Divisões contorno",
            0,
            1000,
            self.divisoes_contorno,
            self.updateDivisoesContorno,
            (
                "Define o número de divisões utilizadas para discretizar "
                "o contorno circular da vara. Um valor maior produz mais "
                "pontos ao redor da circunferência."
            ),
            allow_none=True,
        )

        avancado_layout.addWidget(
            self.divisoes_contorno_input
        )

        # Divisões em Z
        self.divisoes_z_vara_input = self.createAdvancedIntegerInput(
            "Divisões Z Vara",
            0,
            1000,
            self.divisoes_z_vara,
            self.updateDivisoesZVara,
            (
                "Define o número de divisões ao longo do comprimento "
                "da vara no eixo Z. Auto deixa o gerador determinar "
                "a discretização vertical."
            ),
            allow_none=True,
        )

        avancado_layout.addWidget(
            self.divisoes_z_vara_input
        )

        self.avancado_container.setVisible(
            False
        )

        vara_config_layout.addWidget(
            self.avancado_container
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
        self.atualizarResistividadesEstratos()
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

        #potencial
        self.potencial_input = self.createPropertyInput(
            "Potencial V",
            0.0,
            1000000000.0,
            self.potencial,
            self.updatePotencial,
            2,
        )

        scroll_layout.addWidget(
            self.potencial_input
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

    def avisarVaraNaoCentrada(self):

        eixos = []

        if self.dx % 2 == 0:
            eixos.append("X")

        if self.dy % 2 == 0:
            eixos.append("Y")

        if not eixos:
            return

        eixos_texto = " e ".join(eixos)

        QMessageBox.warning(
            self,
            "Vara não exatamente centrada",
            (
                "A malha possui um número par de divisões em X e/ou Y.\n\n"
                "A posição automática foi obtida por truncatura, pelo que "
                "a vara poderá não ficar exatamente no centro do domínio "
                "e as distâncias às fronteiras opostas poderão ser diferentes.\n\n"
                "Verifique a posição da vara na visualização 3D antes de exportar."
            ),
        )

    def createHelpLabel(
            self,
            tooltip,
    ):
        help_label = QLabel("?")

        help_label.setAlignment(
            Qt.AlignCenter
        )

        help_label.setFixedSize(
            20,
            20,
        )

        help_label.setToolTip(
            tooltip
        )

        help_label.setStyleSheet("""
            QLabel {
                color: #93C5FD;
                background-color: #1E293B;
                border: 1px solid #3B82F6;
                border-radius: 10px;
                font-size: 12px;
                font-weight: bold;
            }

            QLabel:hover {
                background-color: #3B82F6;
                color: white;
            }
        """)

        return help_label

    def createAdvancedIntegerInput(
            self,
            text,
            min_value,
            max_value,
            value,
            function,
            tooltip,
            allow_none=False,
    ):
        row = QWidget()

        layout = QHBoxLayout(row)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(8)

        label = QLabel(text)

        spin = QSpinBox()

        if allow_none:
            spin.setRange(
                0,
                max_value,
            )

            spin.setSpecialValueText(
                "Auto"
            )

            if value is None:
                spin.setValue(0)
            else:
                spin.setValue(value)

        else:
            spin.setRange(
                min_value,
                max_value,
            )

            spin.setValue(value)

        spin.setFixedWidth(90)

        self.styleSpinBox(
            spin
        )

        spin.valueChanged.connect(
            function
        )

        help_label = self.createHelpLabel(
            tooltip
        )

        layout.addWidget(
            label,
            1,
        )

        layout.addWidget(
            help_label
        )

        layout.addWidget(
            spin
        )

        row.spin_box = spin

        return row

    def createAdvancedFloatInput(
            self,
            text,
            min_value,
            max_value,
            value,
            function,
            decimals,
            tooltip,
    ):
        row = QWidget()

        layout = QHBoxLayout(row)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(8)

        label = QLabel(text)

        help_label = self.createHelpLabel(
            tooltip
        )

        spin = QDoubleSpinBox()

        spin.setRange(
            min_value,
            max_value,
        )

        spin.setDecimals(
            decimals
        )

        spin.setSingleStep(
            10 ** -decimals
        )

        spin.setValue(
            value
        )

        spin.setFixedWidth(
            90
        )

        self.styleSpinBox(
            spin
        )

        spin.valueChanged.connect(
            function
        )

        layout.addWidget(
            label,
            1,
        )

        layout.addWidget(
            help_label
        )

        layout.addWidget(
            spin
        )

        row.spin_box = spin

        return row



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
    def createPropertyInput(
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

        layout.setSpacing(10)

        label = QLabel(text)
        label.setMinimumWidth(145)

        spin_box = QDoubleSpinBox()

        spin_box.setMinimum(min_value)
        spin_box.setMaximum(max_value)

        spin_box.setDecimals(decimals)

        spin_box.setValue(value)

        spin_box.setFixedWidth(130)

        spin_box.valueChanged.connect(
            function
        )

        spin_box.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #111827;
                color: white;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 5px 22px 5px 8px;
            }

            QDoubleSpinBox:focus {
                border: 2px solid #3B82F6;
                background-color: #0F172A;
            }

            QDoubleSpinBox::up-button,
            QDoubleSpinBox::down-button {
                background-color: #1E293B;
                border: none;
                width: 18px;
            }

            QDoubleSpinBox::up-button:hover,
            QDoubleSpinBox::down-button:hover {
                background-color: #3B82F6;
            }
        """)

        layout.addWidget(
            label,
            1,
        )

        layout.addWidget(
            spin_box
        )

        row.spin_box = spin_box

        return row

    # ==========================================================
    # ESTRATOS
    # ==========================================================

    def lerEstratos(self):

        texto = self.estratos_input.line_edit.text()

        texto = texto.strip()

        if texto == "":
            return [self.sz]

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

    def updatePotencial(self, value):
        self.potencial = value


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

    def atualizarDimensoesPelaFronteira(self):

        if self.avancado_ativo:
            return

        diametro = 2 * self.raio_vara

        tamanho_z=self.comprimento_vara+self.dist_fronteira

        tamanho_xy = (
                2 * self.dist_fronteira
                + diametro
        )

        self.sx = tamanho_xy
        self.sy = tamanho_xy
        self.sz=tamanho_z


        self.wsx.spin_box.blockSignals(True)
        self.wsy.spin_box.blockSignals(True)
        self.wsz.spin_box.blockSignals(True)
        self.wsx.spin_box.setValue(self.sx)
        self.wsy.spin_box.setValue(self.sy)
        self.wsz.spin_box.setValue(self.sz)
        self.wsx.spin_box.blockSignals(False)
        self.wsy.spin_box.blockSignals(False)
        self.wsz.spin_box.blockSignals(False)

        self.gerarMalhaNormal()

    def calcularCuboAutomaticoVara(self):

        cubo_x = self.dx // 2
        cubo_y = self.dy // 2

        return cubo_x, cubo_y
    def updateAvancado(
            self,
            checked,
    ):

        self.avancado_ativo = checked

        self.avancado_container.setVisible(
            checked
        )

        self.dist_fronteira_input.spin_box.setEnabled(
            not checked
        )

        if checked:
            self.dist_fronteira_input.spin_box.setToolTip(
                "A distância automática à fronteira não está "
                "disponível no modo Avançado."
            )
        else:
            self.dist_fronteira_input.spin_box.setToolTip(
                ""
            )

    def updateMaxDiv(
            self,
            value,
    ):
        if value == 0:
            self.max_div = None
        else:
            self.max_div = value

    def updateMinDiv(
            self,
            value,
    ):
        self.min_div = value

    def updateCamadasDeformadas(
            self,
            value,
    ):
        if value == 0:
            self.camadas_deformadas = None
        else:
            self.camadas_deformadas = value

    def updateBallooning(
            self,
            value,
    ):
        self.ballooning = value

    def updateDivisoesXY(
            self,
            value,
    ):
        if value == 0:
            self.divisoes_xy = None
        else:
            self.divisoes_xy = value

    def updateDivisoesContorno(
            self,
            value,
    ):
        if value == 0:
            self.divisoes_contorno = None
        else:
            self.divisoes_contorno = value

    def updateDivisoesZVara(
            self,
            value,
    ):
        if value == 0:
            self.divisoes_z_vara = None
        else:
            self.divisoes_z_vara = value


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

        if not self.avancado_ativo:
            self.atualizarDimensoesPelaFronteira()

    def updateComprimento(
        self,
        value,
    ):

        self.comprimento_vara = value
        self.atualizarDimensoesPelaFronteira()
    def updateDistFronteira(
            self,
            value,
    ):

        if self.avancado_ativo:
            return

        self.dist_fronteira = value

        self.atualizarDimensoesPelaFronteira()

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
            return [self.sz]

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

        # ==========================================================
        # CONDIÇÕES DE FRONTEIRA
        # ==========================================================

        if self.vara_construida:

            vetor = (
                self.malha.gerarVetordaVara(
                    pontos
                )
            )

            tipo_malha = "1Vara"

        else:

            vetor = (
                self.malha.getVetorList()
            )

            tipo_malha = "Normal"

        # ==========================================================
        # SOLO
        # ==========================================================

        estratos = self.lerEstratos()

        if estratos is None:
            return

        resistividades = (
            self.obterResistividadesEstratos()
        )

        # ==========================================================
        # EXPORTADOR
        # ==========================================================

        exportador = ex(
            tetraedros,
            pontos,
            vetor,
            estratos=estratos,
            resistividades=resistividades,
            rho=100,
            v=self.potencial,
        )

        # ==========================================================
        # NOMES
        # ==========================================================

        data_hora = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        dados = (
            f"Div("
            f"{self.malha.dx},"
            f"{self.malha.dy},"
            f"{self.malha.dz}"
            f")"
            f"-Size("
            f"{self.malha.sx},"
            f"{self.malha.sy},"
            f"{self.malha.sz}"
            f")"
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

        try:

            exportador.exportAll(
                nome_elementos,
                nome_pontos,
                nome_vetor,
            )

        except Exception as erro:

            QMessageBox.critical(
                self,
                "Erro de exportação",
                str(erro),
            )

            return

        # ==========================================================
        # MENSAGEM
        # ==========================================================

        mensagem = (
            "Ficheiros exportados com sucesso!\n\n"
            f"Tipo de malha: {tipo_malha}\n"
            f"Pontos: {len(pontos)}\n"
            f"Tetraedros: {len(tetraedros)}\n"
            f"Estratos: {estratos}\n"
            f"Resistividades: {resistividades}\n\n"
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