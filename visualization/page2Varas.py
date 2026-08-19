from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QPushButton,
    QMessageBox,
)

from visualization.page1Vara import Page1Vara
from output.export import Export as ex


class Page2Varas(Page1Vara):

    def __init__(self, voltar):

        # ======================================================
        # VARA 2
        # ======================================================

        self.vara_b_ativa = False

        self.vara_b_x = 0
        self.vara_b_y = 0

        self.raio_vara_b = 0.00794
        self.comprimento_vara_b = 1.0

        # ======================================================
        # AVANÇADO VARA 2
        # ======================================================

        self.avancado_b_ativo = False

        self.max_div_b = None
        self.min_div_b = 1

        self.camadas_deformadas_b = None
        self.ballooning_b = 1.55

        self.divisoes_xy_b = None
        self.divisoes_contorno_b = None
        self.divisoes_z_vara_b = None

        # Distância livre entre as superfícies das varas
        self.distancia_varas = 0.0

        # Informação da última construção
        self.numero_varas_construidas = 0
        self.parametros_varas_construidas = None

        super().__init__(voltar)

        self.configurarInterfaceDuasVaras()


    # ==========================================================
    # INTERFACE
    # ==========================================================

    def configurarInterfaceDuasVaras(self):

        self.alterarTitulo()

        self.alterarTituloVara1()

        self.adicionarSetupVara2()

        self.adicionarDistanciaEntreVaras()

        self.moverBotaoBuild()

        self.atualizarEstadoAutomatico()


    def alterarTitulo(self):

        titulo = self.findChild(
            QLabel,
            "panelTitle",
        )

        if titulo is not None:

            titulo.setText(
                "Malha com duas Varas"
            )


    def alterarTituloVara1(self):

        labels = self.findChildren(
            QLabel
        )

        for label in labels:

            if label.text() == "Setup Vara":

                label.setText(
                    "Setup Vara 1"
                )

                break


    # ==========================================================
    # DISTÂNCIA ENTRE AS VARAS
    # ==========================================================

    def adicionarDistanciaEntreVaras(self):

        self.distancia_varas_input = (
            self.createPreciseFloatInput(
                "Dist. entre varas",
                0.0,
                100000.0,
                self.distancia_varas,
                self.updateDistanciaVaras,
                3,
            )
        )

        self.distancia_varas_input.setToolTip(
            "Distância livre entre as superfícies das duas varas. "
            "No modo automático é utilizada para calcular "
            "as dimensões do domínio e a posição das varas."
        )

        parent = (
            self.dist_fronteira_input
            .parentWidget()
        )

        layout = parent.layout()

        indice = layout.indexOf(
            self.dist_fronteira_input
        )

        layout.insertWidget(
            indice + 1,
            self.distancia_varas_input,
        )


    # ==========================================================
    # SETUP VARA 2
    # ==========================================================

    def adicionarSetupVara2(self):

        parent = (
            self.vara_config
            .parentWidget()
        )

        parent_layout = parent.layout()

        indice_vara_1 = (
            parent_layout.indexOf(
                self.vara_config
            )
        )

        self.vara_b_bloco = QWidget()

        bloco_layout = QVBoxLayout(
            self.vara_b_bloco
        )

        bloco_layout.setContentsMargins(
            0,
            8,
            0,
            0,
        )

        bloco_layout.setSpacing(10)

        # ======================================================
        # CABEÇALHO
        # ======================================================

        cabecalho = QWidget()

        cabecalho_layout = QHBoxLayout(
            cabecalho
        )

        cabecalho_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        titulo = QLabel(
            "Setup Vara 2"
        )

        titulo.setObjectName(
            "sectionTitle"
        )

        self.vara_b_toggle = QCheckBox(
            "OFF"
        )

        self.vara_b_toggle.setChecked(
            False
        )

        self.vara_b_toggle.toggled.connect(
            self.updateVaraBAtiva
        )

        cabecalho_layout.addWidget(
            titulo
        )

        cabecalho_layout.addWidget(
            self.vara_b_toggle
        )

        bloco_layout.addWidget(
            cabecalho
        )

        # ======================================================
        # CONFIGURAÇÃO
        # ======================================================

        self.vara_b_config = QWidget()

        config_layout = QVBoxLayout(
            self.vara_b_config
        )

        config_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        config_layout.setSpacing(10)

        # Raio
        self.raio_b_input = (
            self.createPreciseFloatInput(
                "Raio",
                0.00001,
                self._raioMaximo(
                    self.sx,
                    self.sy,
                ),
                self.raio_vara_b,
                self.updateRaioB,
                5,
            )
        )

        config_layout.addWidget(
            self.raio_b_input
        )

        # Comprimento
        self.comprimento_b_input = (
            self.createPreciseFloatInput(
                "Comprimento",
                0.1,
                self.sz,
                self.comprimento_vara_b,
                self.updateComprimentoB,
                2,
            )
        )

        config_layout.addWidget(
            self.comprimento_b_input
        )

        # ======================================================
        # AVANÇADO
        # ======================================================

        self.avancado_b_checkbox = QCheckBox(
            "Avançado"
        )

        self.avancado_b_checkbox.setChecked(
            False
        )

        self.avancado_b_checkbox.toggled.connect(
            self.updateAvancadoB
        )

        config_layout.addWidget(
            self.avancado_b_checkbox
        )

        self.avancado_b_container = QWidget()

        avancado_layout = QVBoxLayout(
            self.avancado_b_container
        )

        avancado_layout.setContentsMargins(
            10,
            5,
            0,
            5,
        )

        avancado_layout.setSpacing(10)

        # Cubo X
        self.vara_b_x_input = (
            self.createAdvancedIntegerInput(
                "Cubo Vara X",
                0,
                self.dx - 1,
                self.vara_b_x,
                self.updateVaraBX,
                (
                    "Índice do cubo no eixo X onde a Vara 2 "
                    "será colocada."
                ),
            )
        )

        avancado_layout.addWidget(
            self.vara_b_x_input
        )

        # Cubo Y
        self.vara_b_y_input = (
            self.createAdvancedIntegerInput(
                "Cubo Vara Y",
                0,
                self.dy - 1,
                self.vara_b_y,
                self.updateVaraBY,
                (
                    "Índice do cubo no eixo Y onde a Vara 2 "
                    "será colocada."
                ),
            )
        )

        avancado_layout.addWidget(
            self.vara_b_y_input
        )

        # Máximo de divisões
        self.max_div_b_input = (
            self.createAdvancedIntegerInput(
                "Máx. divisões",
                0,
                100,
                self.max_div_b,
                self.updateMaxDivB,
                (
                    "Número máximo de divisões utilizado "
                    "na região deformada da Vara 2."
                ),
                allow_none=True,
            )
        )

        avancado_layout.addWidget(
            self.max_div_b_input
        )

        # Mínimo
        self.min_div_b_input = (
            self.createAdvancedIntegerInput(
                "Mín. divisões",
                1,
                100,
                self.min_div_b,
                self.updateMinDivB,
                (
                    "Número mínimo de divisões utilizado "
                    "na região deformada da Vara 2."
                ),
            )
        )

        avancado_layout.addWidget(
            self.min_div_b_input
        )

        # Camadas
        self.camadas_b_input = (
            self.createAdvancedIntegerInput(
                "Camadas deformadas",
                0,
                100,
                self.camadas_deformadas_b,
                self.updateCamadasB,
                (
                    "Número de camadas entre o contorno da Vara 2 "
                    "e o limite exterior da região deformada."
                ),
                allow_none=True,
            )
        )

        avancado_layout.addWidget(
            self.camadas_b_input
        )

        # Ballooning
        self.ballooning_b_input = (
            self.createAdvancedFloatInput(
                "Ballooning",
                1.0,
                10.0,
                self.ballooning_b,
                self.updateBallooningB,
                2,
                (
                    "Razão de crescimento entre as camadas "
                    "deformadas da Vara 2."
                ),
            )
        )

        avancado_layout.addWidget(
            self.ballooning_b_input
        )

        # Divisões XY
        self.divisoes_xy_b_input = (
            self.createAdvancedIntegerInput(
                "Divisões XY",
                0,
                1000,
                self.divisoes_xy_b,
                self.updateDivisoesXYB,
                (
                    "Número de divisões utilizado no plano XY "
                    "da região especial da Vara 2."
                ),
                allow_none=True,
            )
        )

        avancado_layout.addWidget(
            self.divisoes_xy_b_input
        )

        # Divisões contorno
        self.divisoes_contorno_b_input = (
            self.createAdvancedIntegerInput(
                "Divisões contorno",
                0,
                1000,
                self.divisoes_contorno_b,
                self.updateDivisoesContornoB,
                (
                    "Número de divisões utilizadas para "
                    "discretizar o contorno circular da Vara 2."
                ),
                allow_none=True,
            )
        )

        avancado_layout.addWidget(
            self.divisoes_contorno_b_input
        )

        # Divisões Z
        self.divisoes_z_vara_b_input = (
            self.createAdvancedIntegerInput(
                "Divisões Z Vara",
                0,
                1000,
                self.divisoes_z_vara_b,
                self.updateDivisoesZVaraB,
                (
                    "Número de divisões ao longo do comprimento "
                    "da Vara 2 no eixo Z."
                ),
                allow_none=True,
            )
        )

        avancado_layout.addWidget(
            self.divisoes_z_vara_b_input
        )

        self.avancado_b_container.setVisible(
            False
        )

        config_layout.addWidget(
            self.avancado_b_container
        )

        self.vara_b_config.setVisible(
            False
        )

        bloco_layout.addWidget(
            self.vara_b_config
        )

        parent_layout.insertWidget(
            indice_vara_1 + 1,
            self.vara_b_bloco,
        )


    # ==========================================================
    # MOVER BUILD
    # ==========================================================

    def moverBotaoBuild(self):

        build_button = None

        layout_vara_1 = (
            self.vara_config.layout()
        )

        for i in range(
            layout_vara_1.count()
        ):

            item = (
                layout_vara_1.itemAt(i)
            )

            widget = item.widget()

            if (
                isinstance(
                    widget,
                    QPushButton,
                )
                and widget.text() == "BUILD"
            ):

                build_button = widget

                break

        if build_button is None:
            return

        layout_vara_1.removeWidget(
            build_button
        )

        parent_layout = (
            self.vara_config
            .parentWidget()
            .layout()
        )

        indice_vara_2 = (
            parent_layout.indexOf(
                self.vara_b_bloco
            )
        )

        parent_layout.insertWidget(
            indice_vara_2 + 1,
            build_button,
        )

        self.build_button = (
            build_button
        )


    # ==========================================================
    # ESTADO AUTOMÁTICO
    # ==========================================================

    def modoAvancadoAtivo(self):

        avancado_a = (
            self.vara_ativa
            and self.avancado_ativo
        )

        avancado_b = (
            self.vara_b_ativa
            and self.avancado_b_ativo
        )

        return (
            avancado_a
            or avancado_b
        )


    def geometriaAutomaticaAtiva(self):

        existe_vara = (
            self.vara_ativa
            or self.vara_b_ativa
        )

        return (
            existe_vara
            and not self.modoAvancadoAtivo()
        )


    def atualizarEstadoAutomatico(self):

        if not hasattr(
            self,
            "distancia_varas_input",
        ):
            return

        avancado = (
            self.modoAvancadoAtivo()
        )

        # Só ficam bloqueadas no modo avançado
        self.dist_fronteira_input.spin_box.setEnabled(
            not avancado
        )

        self.distancia_varas_input.spin_box.setEnabled(
            not avancado
        )

        # As dimensões físicas continuam editáveis
        self.wsx.spin_box.setEnabled(
            True
        )

        self.wsy.spin_box.setEnabled(
            True
        )

        self.wsz.spin_box.setEnabled(
            True
        )

        self.fix_size.setEnabled(
            True
        )


    # ==========================================================
    # GEOMETRIA AUTOMÁTICA
    # ==========================================================

    def atualizarGeometriaAutomatica(
        self,
        gerar_malha=True,
    ):

        if not self.geometriaAutomaticaAtiva():
            return

        # Apenas Vara 1
        if (
            self.vara_ativa
            and not self.vara_b_ativa
        ):

            self.calcularGeometriaVara1()

        # Apenas Vara 2
        elif (
            self.vara_b_ativa
            and not self.vara_ativa
        ):

            self.calcularGeometriaVara2()

        # Duas varas
        else:

            self.calcularGeometriaDuasVaras()

        self.atualizarInputsPosicao()

        if gerar_malha:

            self.gerarMalhaNormal()


    # ==========================================================
    # GEOMETRIA DE UMA VARA
    # ==========================================================

    def calcularGeometriaVara1(self):

        L = self.dist_fronteira

        tamanho_xy = (
            2 * self.raio_vara
            + 2 * L
        )

        tamanho_z = (
            self.comprimento_vara
            + L
        )

        self.definirDimensoesFisicas(
            tamanho_xy,
            tamanho_xy,
            tamanho_z,
        )

        self.vara_e_x = (
            self.dx // 2
        )

        self.vara_e_y = (
            self.dy // 2
        )


    def calcularGeometriaVara2(self):

        L = self.dist_fronteira

        tamanho_xy = (
            2 * self.raio_vara_b
            + 2 * L
        )

        tamanho_z = (
            self.comprimento_vara_b
            + L
        )

        self.definirDimensoesFisicas(
            tamanho_xy,
            tamanho_xy,
            tamanho_z,
        )

        self.vara_b_x = (
            self.dx // 2
        )

        self.vara_b_y = (
            self.dy // 2
        )


    # ==========================================================
    # CENTRO DE UM CUBO
    # ==========================================================

    def centroDoCubo(
        self,
        indice,
        tamanho,
        divisoes,
    ):

        tamanho_cubo = (
            tamanho / divisoes
        )

        return (
            indice + 0.5
        ) * tamanho_cubo


    # ==========================================================
    # CUBO CENTRAL
    # ==========================================================

    def calcularCuboCentral(
        self,
        tamanho,
        divisoes,
    ):

        if divisoes <= 1:
            return 0

        centro_dominio = (
            tamanho / 2
        )

        melhor_cubo = 0
        menor_distancia = float(
            "inf"
        )

        for cubo in range(
            divisoes
        ):

            centro = (
                self.centroDoCubo(
                    cubo,
                    tamanho,
                    divisoes,
                )
            )

            distancia = abs(
                centro
                - centro_dominio
            )

            if distancia < menor_distancia:

                menor_distancia = (
                    distancia
                )

                melhor_cubo = cubo

        return melhor_cubo


    # ==========================================================
    # CALCULAR PAR DE CUBOS PARA AS DUAS VARAS
    # ==========================================================

    def calcularCubosAutomaticosDuasVaras(
        self,
        tamanho,
        divisoes,
    ):

        if divisoes < 2:

            raise ValueError(
                "São necessárias pelo menos 2 divisões "
                "no eixo onde serão colocadas as duas varas."
            )

        L = self.dist_fronteira
        D = self.distancia_varas

        r_a = self.raio_vara
        r_b = self.raio_vara_b

        melhor_cubo_a = None
        melhor_cubo_b = None

        menor_erro = float(
            "inf"
        )

        # Testa todos os pares de cubos possíveis
        for cubo_a in range(
            divisoes - 1
        ):

            centro_a = (
                self.centroDoCubo(
                    cubo_a,
                    tamanho,
                    divisoes,
                )
            )

            for cubo_b in range(
                cubo_a + 1,
                divisoes,
            ):

                centro_b = (
                    self.centroDoCubo(
                        cubo_b,
                        tamanho,
                        divisoes,
                    )
                )

                # Distância da superfície da Vara A
                # à primeira fronteira
                distancia_fronteira_a = (
                    centro_a
                    - r_a
                )

                # Distância livre entre as duas superfícies
                distancia_entre_varas = (
                    centro_b
                    - centro_a
                    - r_a
                    - r_b
                )

                # Distância da superfície da Vara B
                # à última fronteira
                distancia_fronteira_b = (
                    tamanho
                    - centro_b
                    - r_b
                )

                erro_fronteira_a = abs(
                    distancia_fronteira_a
                    - L
                )

                erro_varas = abs(
                    distancia_entre_varas
                    - D
                )

                erro_fronteira_b = abs(
                    distancia_fronteira_b
                    - L
                )

                erro_total = (
                    erro_fronteira_a
                    + erro_varas
                    + erro_fronteira_b
                )

                if erro_total < menor_erro:

                    menor_erro = (
                        erro_total
                    )

                    melhor_cubo_a = (
                        cubo_a
                    )

                    melhor_cubo_b = (
                        cubo_b
                    )

        return (
            melhor_cubo_a,
            melhor_cubo_b,
        )


    # ==========================================================
    # POSIÇÕES AUTOMÁTICAS SEM ALTERAR SIZE
    # ==========================================================

    def atualizarPosicoesAutomaticas(self):

        if not self.geometriaAutomaticaAtiva():
            return

        # Apenas Vara 1
        if (
            self.vara_ativa
            and not self.vara_b_ativa
        ):

            self.vara_e_x = (
                self.dx // 2
            )

            self.vara_e_y = (
                self.dy // 2
            )

        # Apenas Vara 2
        elif (
            self.vara_b_ativa
            and not self.vara_ativa
        ):

            self.vara_b_x = (
                self.dx // 2
            )

            self.vara_b_y = (
                self.dy // 2
            )

        # Duas varas
        else:

            self.calcularPosicoesAutomaticasDuasVaras()

        self.atualizarInputsPosicao()


    # ==========================================================
    # POSICIONAR DUAS VARAS
    # ==========================================================

    def calcularPosicoesAutomaticasDuasVaras(self):

        # Mais divisões em X
        if self.dx >= self.dy:

            (
                self.vara_e_x,
                self.vara_b_x,
            ) = (
                self.calcularCubosAutomaticosDuasVaras(
                    self.sx,
                    self.dx,
                )
            )

            cubo_y = (
                self.calcularCuboCentral(
                    self.sy,
                    self.dy,
                )
            )

            self.vara_e_y = (
                cubo_y
            )

            self.vara_b_y = (
                cubo_y
            )

        # Mais divisões em Y
        else:

            (
                self.vara_e_y,
                self.vara_b_y,
            ) = (
                self.calcularCubosAutomaticosDuasVaras(
                    self.sy,
                    self.dy,
                )
            )

            cubo_x = (
                self.calcularCuboCentral(
                    self.sx,
                    self.dx,
                )
            )

            self.vara_e_x = (
                cubo_x
            )

            self.vara_b_x = (
                cubo_x
            )


    # ==========================================================
    # GEOMETRIA DE DUAS VARAS
    # ==========================================================

    def calcularGeometriaDuasVaras(self):

        L = self.dist_fronteira
        D = self.distancia_varas

        r_a = self.raio_vara
        r_b = self.raio_vara_b

        comprimento_a = (
            self.comprimento_vara
        )

        comprimento_b = (
            self.comprimento_vara_b
        )

        # Dimensão do eixo onde estão as duas varas
        tamanho_principal = (
            2 * r_a
            + 2 * r_b
            + D
            + 2 * L
        )

        # Dimensão perpendicular
        tamanho_secundario = (
            2 * max(
                r_a,
                r_b,
            )
            + 2 * L
        )

        # Z usa o maior comprimento
        tamanho_z = (
            max(
                comprimento_a,
                comprimento_b,
            )
            + L
        )

        # ======================================================
        # VARAS DISTRIBUÍDAS EM X
        # ======================================================

        if self.dx >= self.dy:

            self.definirDimensoesFisicas(
                tamanho_principal,
                tamanho_secundario,
                tamanho_z,
            )

        # ======================================================
        # VARAS DISTRIBUÍDAS EM Y
        # ======================================================

        else:

            self.definirDimensoesFisicas(
                tamanho_secundario,
                tamanho_principal,
                tamanho_z,
            )

        # Depois de conhecer os tamanhos,
        # escolhe os melhores cubos
        self.calcularPosicoesAutomaticasDuasVaras()


    # ==========================================================
    # DEFINIR DIMENSÕES
    # ==========================================================

    def definirDimensoesFisicas(
        self,
        tamanho_x,
        tamanho_y,
        tamanho_z,
    ):

        self.sx = tamanho_x
        self.sy = tamanho_y
        self.sz = tamanho_z

        widgets = (
            (
                self.wsx,
                self.sx,
            ),
            (
                self.wsy,
                self.sy,
            ),
            (
                self.wsz,
                self.sz,
            ),
        )

        for widget, valor in widgets:

            spin = (
                widget.spin_box
            )

            spin.blockSignals(
                True
            )

            if valor > spin.maximum():

                spin.setMaximum(
                    valor
                )

            spin.setValue(
                valor
            )

            spin.blockSignals(
                False
            )


    # ==========================================================
    # ATUALIZAR INPUTS DA POSIÇÃO
    # ==========================================================

    def atualizarInputsPosicao(self):

        inputs = (
            (
                getattr(
                    self,
                    "vara_x_spin",
                    None,
                ),
                self.vara_e_x,
            ),
            (
                getattr(
                    self,
                    "vara_y_spin",
                    None,
                ),
                self.vara_e_y,
            ),
            (
                getattr(
                    self,
                    "vara_b_x_input",
                    None,
                ),
                self.vara_b_x,
            ),
            (
                getattr(
                    self,
                    "vara_b_y_input",
                    None,
                ),
                self.vara_b_y,
            ),
        )

        for widget, valor in inputs:

            if widget is None:
                continue

            spin = (
                widget.spin_box
            )

            spin.blockSignals(
                True
            )

            spin.setValue(
                valor
            )

            spin.blockSignals(
                False
            )


    # ==========================================================
    # DISTÂNCIAS REAIS OBTIDAS
    # ==========================================================

    def obterDistanciasReaisDuasVaras(self):

        if (
            not self.vara_ativa
            or not self.vara_b_ativa
        ):

            return None

        # ======================================================
        # VARAS EM X
        # ======================================================

        if self.dx >= self.dy:

            centro_a = (
                self.centroDoCubo(
                    self.vara_e_x,
                    self.sx,
                    self.dx,
                )
            )

            centro_b = (
                self.centroDoCubo(
                    self.vara_b_x,
                    self.sx,
                    self.dx,
                )
            )

            fronteira_a = (
                centro_a
                - self.raio_vara
            )

            entre_varas = (
                centro_b
                - centro_a
                - self.raio_vara
                - self.raio_vara_b
            )

            fronteira_b = (
                self.sx
                - centro_b
                - self.raio_vara_b
            )

        # ======================================================
        # VARAS EM Y
        # ======================================================

        else:

            centro_a = (
                self.centroDoCubo(
                    self.vara_e_y,
                    self.sy,
                    self.dy,
                )
            )

            centro_b = (
                self.centroDoCubo(
                    self.vara_b_y,
                    self.sy,
                    self.dy,
                )
            )

            fronteira_a = (
                centro_a
                - self.raio_vara
            )

            entre_varas = (
                centro_b
                - centro_a
                - self.raio_vara
                - self.raio_vara_b
            )

            fronteira_b = (
                self.sy
                - centro_b
                - self.raio_vara_b
            )

        return (
            fronteira_a,
            entre_varas,
            fronteira_b,
        )


    # ==========================================================
    # AVISO DE POSICIONAMENTO
    # ==========================================================

    def avisarPosicionamentoAutomatico(self):

        if not self.geometriaAutomaticaAtiva():
            return

        if (
            not self.vara_ativa
            or not self.vara_b_ativa
        ):

            self.avisarVaraNaoCentrada()
            return

        distancias = (
            self.obterDistanciasReaisDuasVaras()
        )

        if distancias is None:
            return

        (
            fronteira_a,
            entre_varas,
            fronteira_b,
        ) = distancias

        erro_a = abs(
            fronteira_a
            - self.dist_fronteira
        )

        erro_varas = abs(
            entre_varas
            - self.distancia_varas
        )

        erro_b = abs(
            fronteira_b
            - self.dist_fronteira
        )

        erro_maximo = max(
            erro_a,
            erro_varas,
            erro_b,
        )

        if erro_maximo <= 0.000001:
            return

        eixo = (
            "X"
            if self.dx >= self.dy
            else "Y"
        )

        QMessageBox.warning(
            self,
            "Posicionamento aproximado das varas",
            (
                "A discretização atual não permite obter exatamente "
                "todas as distâncias configuradas.\n\n"

                f"Eixo utilizado: {eixo}\n\n"

                f"Distância à fronteira pretendida: "
                f"{self.dist_fronteira:.3f} m\n"

                f"Distância Vara 1 → fronteira: "
                f"{fronteira_a:.3f} m\n"

                f"Distância entre varas pretendida: "
                f"{self.distancia_varas:.3f} m\n"

                f"Distância entre varas obtida: "
                f"{entre_varas:.3f} m\n"

                f"Distância Vara 2 → fronteira: "
                f"{fronteira_b:.3f} m\n\n"

                "Foi escolhido automaticamente o par de cubos "
                "que produz o menor erro total.\n\n"

                "Verifique visualmente a posição das varas "
                "antes de exportar."
            ),
        )


    # ==========================================================
    # VARA 1
    # ==========================================================

    def updateVaraAtiva(
        self,
        checked,
    ):

        self.vara_ativa = checked

        if checked:

            self.vara_toggle.setText(
                "ON"
            )

        else:

            self.vara_toggle.setText(
                "OFF"
            )

        self.vara_config.setVisible(
            checked
        )

        self.atualizarEstadoAutomatico()

        # Ligar/desligar não altera os Size
        self.gerarMalhaNormal()


    def updateRaio(
        self,
        value,
    ):

        self.raio_vara = value

        if self.geometriaAutomaticaAtiva():

            self.atualizarGeometriaAutomatica()


    def updateComprimento(
        self,
        value,
    ):

        self.comprimento_vara = value

        if self.geometriaAutomaticaAtiva():

            self.atualizarGeometriaAutomatica()


    # ==========================================================
    # VARA 2
    # ==========================================================

    def updateVaraBAtiva(
        self,
        checked,
    ):

        self.vara_b_ativa = checked

        if checked:

            self.vara_b_toggle.setText(
                "ON"
            )

        else:

            self.vara_b_toggle.setText(
                "OFF"
            )

        self.vara_b_config.setVisible(
            checked
        )

        self.atualizarEstadoAutomatico()

        # Ligar/desligar não altera os Size
        self.gerarMalhaNormal()


    def updateVaraBX(
        self,
        value,
    ):

        self.vara_b_x = value


    def updateVaraBY(
        self,
        value,
    ):

        self.vara_b_y = value


    def updateRaioB(
        self,
        value,
    ):

        self.raio_vara_b = value

        if self.geometriaAutomaticaAtiva():

            self.atualizarGeometriaAutomatica()


    def updateComprimentoB(
        self,
        value,
    ):

        self.comprimento_vara_b = value

        if self.geometriaAutomaticaAtiva():

            self.atualizarGeometriaAutomatica()


    # ==========================================================
    # DISTÂNCIAS
    # ==========================================================

    def updateDistFronteira(
        self,
        value,
    ):

        if self.modoAvancadoAtivo():
            return

        self.dist_fronteira = value

        if self.geometriaAutomaticaAtiva():

            self.atualizarGeometriaAutomatica()


    def updateDistanciaVaras(
        self,
        value,
    ):

        if self.modoAvancadoAtivo():
            return

        self.distancia_varas = value

        if (
            self.vara_ativa
            and self.vara_b_ativa
            and self.geometriaAutomaticaAtiva()
        ):

            self.atualizarGeometriaAutomatica()


    # ==========================================================
    # AVANÇADO VARA 1
    # ==========================================================

    def updateAvancado(
        self,
        checked,
    ):

        self.avancado_ativo = checked

        self.avancado_container.setVisible(
            checked
        )

        self.atualizarEstadoAutomatico()

        if not checked:

            self.atualizarPosicoesAutomaticas()

        self.gerarMalhaNormal()


    # ==========================================================
    # AVANÇADO VARA 2
    # ==========================================================

    def updateAvancadoB(
        self,
        checked,
    ):

        self.avancado_b_ativo = checked

        self.avancado_b_container.setVisible(
            checked
        )

        self.atualizarEstadoAutomatico()

        if not checked:

            self.atualizarPosicoesAutomaticas()

        self.gerarMalhaNormal()


    def updateMaxDivB(
        self,
        value,
    ):

        if value == 0:

            self.max_div_b = None

        else:

            self.max_div_b = value


    def updateMinDivB(
        self,
        value,
    ):

        self.min_div_b = value


    def updateCamadasB(
        self,
        value,
    ):

        if value == 0:

            self.camadas_deformadas_b = None

        else:

            self.camadas_deformadas_b = value


    def updateBallooningB(
        self,
        value,
    ):

        self.ballooning_b = value


    def updateDivisoesXYB(
        self,
        value,
    ):

        if value == 0:

            self.divisoes_xy_b = None

        else:

            self.divisoes_xy_b = value


    def updateDivisoesContornoB(
        self,
        value,
    ):

        if value == 0:

            self.divisoes_contorno_b = None

        else:

            self.divisoes_contorno_b = value


    def updateDivisoesZVaraB(
        self,
        value,
    ):

        if value == 0:

            self.divisoes_z_vara_b = None

        else:

            self.divisoes_z_vara_b = value


    # ==========================================================
    # LIMITES DA VARA 2
    # ==========================================================

    def ajustarParametrosVaraB(self):

        tamanho_x, tamanho_y, tamanho_z = (
            self.obterTamanhosDaMalha()
        )

        raio_maximo = (
            self._raioMaximo(
                tamanho_x,
                tamanho_y,
            )
        )

        if self.raio_vara_b > raio_maximo:

            self.raio_vara_b = (
                raio_maximo
            )

        self.raio_b_input.spin_box.blockSignals(
            True
        )

        self.raio_b_input.spin_box.setMaximum(
            raio_maximo
        )

        self.raio_b_input.spin_box.setValue(
            self.raio_vara_b
        )

        self.raio_b_input.spin_box.blockSignals(
            False
        )

        if self.comprimento_vara_b > tamanho_z:

            self.comprimento_vara_b = (
                tamanho_z
            )

        self.comprimento_b_input.spin_box.blockSignals(
            True
        )

        self.comprimento_b_input.spin_box.setMaximum(
            tamanho_z
        )

        self.comprimento_b_input.spin_box.setValue(
            self.comprimento_vara_b
        )

        self.comprimento_b_input.spin_box.blockSignals(
            False
        )


    # ==========================================================
    # BUILD
    # ==========================================================

    def buildVara(self):

        if (
            not self.vara_ativa
            and not self.vara_b_ativa
        ):

            self.gerarMalhaNormal()

            return

        # ======================================================
        # VALIDAÇÃO VARA 1
        # ======================================================

        if (
            self.vara_ativa
            and self.avancado_ativo
            and self.max_div is not None
            and self.max_div < self.min_div
        ):

            QMessageBox.warning(
                self,
                "Configuração inválida",
                (
                    "Na Vara 1, Máx. divisões não pode "
                    "ser inferior a Mín. divisões."
                ),
            )

            return

        # ======================================================
        # VALIDAÇÃO VARA 2
        # ======================================================

        if (
            self.vara_b_ativa
            and self.avancado_b_ativo
            and self.max_div_b is not None
            and self.max_div_b < self.min_div_b
        ):

            QMessageBox.warning(
                self,
                "Configuração inválida",
                (
                    "Na Vara 2, Máx. divisões não pode "
                    "ser inferior a Mín. divisões."
                ),
            )

            return

        # ======================================================
        # ESTRATOS
        # ======================================================

        estratos = (
            self.lerEstratos()
        )

        if estratos is None:
            return

        self.estratos = (
            estratos
        )

        self.resistividades_estratos = (
            self.obterResistividadesEstratos()
        )

        # Cria a malha com os Size atualmente apresentados
        self.criarObjetoMalha()

        self.ajustarParametrosVaraB()

        # ======================================================
        # CALCULA APENAS AS POSIÇÕES
        # NÃO ALTERA OS SIZE NO BUILD
        # ======================================================

        if self.geometriaAutomaticaAtiva():

            try:

                self.atualizarPosicoesAutomaticas()

            except Exception as erro:

                QMessageBox.warning(
                    self,
                    "Posicionamento das varas",
                    str(erro),
                )

                return

        try:

            # Duas varas
            if (
                self.vara_ativa
                and self.vara_b_ativa
            ):

                self.gerarDuasVaras()

            # Apenas Vara 1
            elif self.vara_ativa:

                self.gerarApenasVara1()

            # Apenas Vara 2
            elif self.vara_b_ativa:

                self.gerarApenasVara2()

        except Exception as erro:

            QMessageBox.critical(
                self,
                "Erro ao construir malha",
                str(erro),
            )

            return

        self.vara_construida = True

        self.guardarParametrosDaConstrucao()

        self.updateViewer()

        self.avisarPosicionamentoAutomatico()


    # ==========================================================
    # GERAR APENAS VARA 1
    # ==========================================================

    def gerarApenasVara1(self):

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

                divisoes_xy=(
                    self.divisoes_xy
                ),

                divisoes_contorno=(
                    self.divisoes_contorno
                ),

                divisoes_z_vara=(
                    self.divisoes_z_vara
                ),

                automatico=(
                    not self.avancado_ativo
                ),

                estrato=(
                    self.estratos
                ),

            )
        )

        self.guardarMalhaGerada(
            pontos,
            cubos,
            normais,
            deformados,
        )

        self.numero_varas_construidas = (
            1
        )


    # ==========================================================
    # GERAR APENAS VARA 2
    # ==========================================================

    def gerarApenasVara2(self):

        pontos, cubos, normais, deformados = (
            self.malha.gerarMalha1Vara(
                self.vara_b_x,
                self.vara_b_y,
                self.raio_vara_b,
                self.comprimento_vara_b,

                self.max_div_b,
                self.min_div_b,
                self.camadas_deformadas_b,
                self.ballooning_b,

                divisoes_xy=(
                    self.divisoes_xy_b
                ),

                divisoes_contorno=(
                    self.divisoes_contorno_b
                ),

                divisoes_z_vara=(
                    self.divisoes_z_vara_b
                ),

                automatico=(
                    not self.avancado_b_ativo
                ),

                estrato=(
                    self.estratos
                ),


            )
        )

        self.guardarMalhaGerada(
            pontos,
            cubos,
            normais,
            deformados,
        )

        self.numero_varas_construidas = (
            1
        )


    # ==========================================================
    # GERAR DUAS VARAS
    # ==========================================================

    def gerarDuasVaras(self):

        mesma_posicao = (
            self.vara_e_x == self.vara_b_x
            and self.vara_e_y == self.vara_b_y
        )

        if mesma_posicao:

            raise ValueError(
                "As duas varas ficaram no mesmo cubo. "
                "Aumente o número de divisões no eixo onde "
                "as varas serão distribuídas."
            )

        (
            pontos,
            cubos,
            normais,
            deformados_a,
            deformados_b,
        ) = (
            self.malha.gerarMalha2Vara(
                self.vara_e_x,
                self.vara_e_y,
                self.raio_vara,
                self.comprimento_vara,

                self.max_div,
                self.min_div,
                self.camadas_deformadas,
                self.ballooning,

                self.vara_b_x,
                self.vara_b_y,
                self.raio_vara_b,
                self.comprimento_vara_b,

                self.max_div_b,
                self.min_div_b,
                self.camadas_deformadas_b,
                self.ballooning_b,

                automatico=(
                    not self.modoAvancadoAtivo()
                ),

                estrato=(
                    self.estratos
                ),


            )
        )

        deformados = (
            list(
                deformados_a
            )
            +
            list(
                deformados_b
            )
        )

        self.guardarMalhaGerada(
            pontos,
            cubos,
            normais,
            deformados,
        )

        self.numero_varas_construidas = (
            2
        )


    # ==========================================================
    # GUARDAR MALHA
    # ==========================================================

    def guardarMalhaGerada(
        self,
        pontos,
        cubos,
        normais,
        deformados,
    ):

        self.malha.points_list = (
            pontos
        )

        self.malha.cube_list = (
            cubos
        )

        self.malha.final_points_list = (
            pontos
        )

        self.malha.final_cube_list = (
            cubos
        )

        self.cubos_normais = (
            normais
        )

        self.cubos_deformados = (
            deformados
        )


    # ==========================================================
    # GUARDAR PARÂMETROS
    # ==========================================================

    def guardarParametrosDaConstrucao(self):

        dados = {

            "estratos": (
                self.estratos.copy()
            ),

            "resistividades": (
                self.resistividades_estratos.copy()
            ),

            "dist_fronteira": (
                self.dist_fronteira
            ),

            "distancia_varas": (
                self.distancia_varas
            ),
        }

        if self.vara_ativa:

            dados["vara_1"] = {

                "x": (
                    self.vara_e_x
                ),

                "y": (
                    self.vara_e_y
                ),

                "raio": (
                    self.raio_vara
                ),

                "comprimento": (
                    self.comprimento_vara
                ),

                "avancado": (
                    self.avancado_ativo
                ),
            }

        if self.vara_b_ativa:

            dados["vara_2"] = {

                "x": (
                    self.vara_b_x
                ),

                "y": (
                    self.vara_b_y
                ),

                "raio": (
                    self.raio_vara_b
                ),

                "comprimento": (
                    self.comprimento_vara_b
                ),

                "avancado": (
                    self.avancado_b_ativo
                ),
            }

        self.parametros_varas_construidas = (
            dados
        )


    # ==========================================================
    # MALHA NORMAL
    # ==========================================================

    def gerarMalhaNormal(self):

        super().gerarMalhaNormal()

        self.numero_varas_construidas = (
            0
        )

        self.parametros_varas_construidas = (
            None
        )


    # ==========================================================
    # DIV-X
    # ==========================================================

    def updateDx(
        self,
        value,
    ):

        self.dx = value

        if self.vara_e_x >= self.dx:

            self.vara_e_x = (
                self.dx - 1
            )

        self.vara_x_spin.spin_box.setMaximum(
            self.dx - 1
        )

        self.vara_x_spin.spin_box.setValue(
            self.vara_e_x
        )

        if hasattr(
            self,
            "vara_b_x_input",
        ):

            if self.vara_b_x >= self.dx:

                self.vara_b_x = (
                    self.dx - 1
                )

            self.vara_b_x_input.spin_box.setMaximum(
                self.dx - 1
            )

            self.vara_b_x_input.spin_box.setValue(
                self.vara_b_x
            )

        if self.geometriaAutomaticaAtiva():

            try:

                self.atualizarGeometriaAutomatica()

            except ValueError:

                self.gerarMalhaNormal()

        else:

            self.gerarMalhaNormal()


    # ==========================================================
    # DIV-Y
    # ==========================================================

    def updateDy(
        self,
        value,
    ):

        self.dy = value

        if self.vara_e_y >= self.dy:

            self.vara_e_y = (
                self.dy - 1
            )

        self.vara_y_spin.spin_box.setMaximum(
            self.dy - 1
        )

        self.vara_y_spin.spin_box.setValue(
            self.vara_e_y
        )

        if hasattr(
            self,
            "vara_b_y_input",
        ):

            if self.vara_b_y >= self.dy:

                self.vara_b_y = (
                    self.dy - 1
                )

            self.vara_b_y_input.spin_box.setMaximum(
                self.dy - 1
            )

            self.vara_b_y_input.spin_box.setValue(
                self.vara_b_y
            )

        if self.geometriaAutomaticaAtiva():

            try:

                self.atualizarGeometriaAutomatica()

            except ValueError:

                self.gerarMalhaNormal()

        else:

            self.gerarMalhaNormal()


    # ==========================================================
    # DIV-Z
    # ==========================================================

    def updateDz(
        self,
        value,
    ):

        self.dz = value

        self.gerarMalhaNormal()


    # ==========================================================
    # SIZE-X
    # ==========================================================

    def updateSx(
        self,
        value,
    ):

        self.sx = value

        if self.geometriaAutomaticaAtiva():

            try:

                self.atualizarPosicoesAutomaticas()

            except ValueError:
                pass

        self.gerarMalhaNormal()

        if hasattr(
            self,
            "raio_b_input",
        ):

            self.ajustarParametrosVaraB()


    # ==========================================================
    # SIZE-Y
    # ==========================================================

    def updateSy(
        self,
        value,
    ):

        self.sy = value

        if self.geometriaAutomaticaAtiva():

            try:

                self.atualizarPosicoesAutomaticas()

            except ValueError:
                pass

        self.gerarMalhaNormal()

        if hasattr(
            self,
            "raio_b_input",
        ):

            self.ajustarParametrosVaraB()


    # ==========================================================
    # SIZE-Z
    # ==========================================================

    def updateSz(
        self,
        value,
    ):

        self.sz = value

        self.gerarMalhaNormal()

        if hasattr(
            self,
            "comprimento_b_input",
        ):

            self.ajustarParametrosVaraB()


    # ==========================================================
    # SYNC
    # ==========================================================

    def updateFixSize(
        self,
        checked,
        widget1,
        widget2,
        widget3,
    ):

        super().updateFixSize(
            checked,
            widget1,
            widget2,
            widget3,
        )

        if hasattr(
            self,
            "raio_b_input",
        ):

            self.ajustarParametrosVaraB()


    # ==========================================================
    # EXPORTAÇÃO
    # ==========================================================

    def export(self):

        tetraedros, pontos = (
            self.malha.clean(
                self.malha.getCubesList(),
                self.malha.getPointsList(),
            )
        )

        # ======================================================
        # CONDIÇÕES DE FRONTEIRA
        # ======================================================

        if self.vara_construida:

            vetor = (
                self.malha.gerarVetordaVara(
                    pontos
                )
            )

        else:

            vetor = (
                self.malha.getVetorList()
            )

        # ======================================================
        # TIPO DE MALHA
        # ======================================================

        if self.numero_varas_construidas == 2:

            tipo_malha = (
                "2Varas"
            )

        elif self.numero_varas_construidas == 1:

            tipo_malha = (
                "1Vara"
            )

        else:

            tipo_malha = (
                "Normal"
            )

        # ======================================================
        # SOLO
        # ======================================================

        estratos = (
            self.lerEstratos()
        )

        if estratos is None:
            return

        resistividades = (
            self.obterResistividadesEstratos()
        )

        # ======================================================
        # EXPORTADOR
        # ======================================================

        exportador = ex(
            tetraedros,
            pontos,
            vetor,
            estratos=estratos,
            resistividades=resistividades,
            rho=100,
            v=self.potencial,
        )

        # ======================================================
        # NOMES
        # ======================================================

        data_hora = (
            datetime.now().strftime(
                "%Y-%m-%d_%H-%M-%S"
            )
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

        # ======================================================
        # MENSAGEM
        # ======================================================

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