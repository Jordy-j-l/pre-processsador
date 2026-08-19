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

        # A distância entre as varas é um resultado da geometria.
        # O utilizador pode consultar o valor, mas não alterá-lo.
        self.distancia_varas_input.spin_box.setReadOnly(True)

        self.distancia_varas_input.setToolTip(
            "Distância livre entre as superfícies das duas varas. "
            "Este valor é calculado automaticamente a partir das "
            "divisões da malha, dos raios e da distância à fronteira."
        )

        parent = self.dist_fronteira_input.parentWidget()
        layout = parent.layout()
        indice = layout.indexOf(self.dist_fronteira_input)

        layout.insertWidget(
            indice + 1,
            self.distancia_varas_input,
        )

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

        if not hasattr(self, "distancia_varas_input"):
            return

        avancado = self.modoAvancadoAtivo()

        self.dist_fronteira_input.spin_box.setEnabled(
            not avancado
        )

        # É sempre apenas informativa.
        self.distancia_varas_input.spin_box.setEnabled(True)
        self.distancia_varas_input.spin_box.setReadOnly(True)

        self.wsx.spin_box.setEnabled(True)
        self.wsy.spin_box.setEnabled(True)
        self.wsz.spin_box.setEnabled(True)

        self.fix_size.setEnabled(True)

    def atualizarGeometriaAutomatica(
        self,
        gerar_malha=True,
        mostrar_erro=True,
    ):

        if not self.geometriaAutomaticaAtiva():
            return True

        try:

            if self.vara_ativa and not self.vara_b_ativa:
                self.calcularGeometriaVara1()

            elif self.vara_b_ativa and not self.vara_ativa:
                self.calcularGeometriaVara2()

            else:
                self.calcularGeometriaDuasVaras()

            self.atualizarInputsPosicao()

        except ValueError as erro:

            if mostrar_erro:
                QMessageBox.warning(
                    self,
                    "Configuração das varas",
                    str(erro),
                )

            if gerar_malha:
                self.gerarMalhaNormal()

            return False

        if gerar_malha:
            self.gerarMalhaNormal()

        return True

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
        divisoes,
    ):

        if divisoes < 2:
            raise ValueError(
                "São necessárias pelo menos 2 divisões "
                "no eixo onde serão colocadas as duas varas."
            )

        meio = divisoes // 2

        # Par: usa os dois cubos centrais.
        # 0 | 1 | 2 | 3
        #     A   B
        if divisoes % 2 == 0:
            cubo_a = meio - 1
            cubo_b = meio

        # Ímpar: deixa o cubo central entre as duas varas.
        # 0 | 1 | 2 | 3 | 4
        #     A       B
        else:
            cubo_a = meio - 1
            cubo_b = meio + 1

        return cubo_a, cubo_b

    def calcularTamanhoEixoDasVaras(
        self,
        divisoes,
        cubo_a,
        cubo_b,
    ):

        L = self.dist_fronteira
        r_a = self.raio_vara
        r_b = self.raio_vara_b

        # Centro da Vara 1 = (cubo_a + 0.5) * tamanho_cubo.
        # Para garantir centro - raio >= L:
        fator_esquerda = cubo_a + 0.5

        # Distância da Vara 2 à fronteira oposta.
        fator_direita = divisoes - cubo_b - 0.5

        tamanho_cubo_esquerda = (
            (L + r_a) / fator_esquerda
        )

        tamanho_cubo_direita = (
            (L + r_b) / fator_direita
        )

        # Garante também que cada círculo cabe no cubo onde
        # será criada a região deformada.
        tamanho_cubo_vara = (
            2 * max(r_a, r_b) + 0.00002
        )

        tamanho_cubo = max(
            tamanho_cubo_esquerda,
            tamanho_cubo_direita,
            tamanho_cubo_vara,
        )

        return tamanho_cubo * divisoes

    def calcularTamanhoEixoPerpendicular(
        self,
        divisoes,
        cubo,
    ):

        if divisoes < 1:
            raise ValueError(
                "O eixo perpendicular deve ter pelo menos 1 divisão."
            )

        L = self.dist_fronteira
        raio = max(
            self.raio_vara,
            self.raio_vara_b,
        )

        fator_inicio = cubo + 0.5
        fator_fim = divisoes - cubo - 0.5

        tamanho_cubo_inicio = (
            (L + raio) / fator_inicio
        )

        tamanho_cubo_fim = (
            (L + raio) / fator_fim
        )

        tamanho_cubo_vara = (
            2 * raio + 0.00002
        )

        tamanho_cubo = max(
            tamanho_cubo_inicio,
            tamanho_cubo_fim,
            tamanho_cubo_vara,
        )

        return tamanho_cubo * divisoes

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

        eixo = self.obterEixoAutomaticoDuasVaras()
        self.eixo_varas = eixo

        if eixo == "X":

            self.vara_e_x, self.vara_b_x = (
                self.calcularCubosAutomaticosDuasVaras(
                    self.dx
                )
            )

            cubo_y = self.calcularCuboCentral(
                self.sy,
                self.dy,
            )

            self.vara_e_y = cubo_y
            self.vara_b_y = cubo_y

        else:

            self.vara_e_y, self.vara_b_y = (
                self.calcularCubosAutomaticosDuasVaras(
                    self.dy
                )
            )

            cubo_x = self.calcularCuboCentral(
                self.sx,
                self.dx,
            )

            self.vara_e_x = cubo_x
            self.vara_b_x = cubo_x

    def calcularGeometriaDuasVaras(self):

        L = self.dist_fronteira

        eixo = self.obterEixoAutomaticoDuasVaras()
        self.eixo_varas = eixo

        if eixo == "X":

            cubo_a, cubo_b = (
                self.calcularCubosAutomaticosDuasVaras(
                    self.dx
                )
            )

            cubo_perpendicular = self.calcularCuboCentral(
                self.sy,
                self.dy,
            )

            tamanho_x = self.calcularTamanhoEixoDasVaras(
                self.dx,
                cubo_a,
                cubo_b,
            )

            tamanho_y = self.calcularTamanhoEixoPerpendicular(
                self.dy,
                cubo_perpendicular,
            )

            self.vara_e_x = cubo_a
            self.vara_b_x = cubo_b

            self.vara_e_y = cubo_perpendicular
            self.vara_b_y = cubo_perpendicular

        else:

            cubo_a, cubo_b = (
                self.calcularCubosAutomaticosDuasVaras(
                    self.dy
                )
            )

            cubo_perpendicular = self.calcularCuboCentral(
                self.sx,
                self.dx,
            )

            tamanho_y = self.calcularTamanhoEixoDasVaras(
                self.dy,
                cubo_a,
                cubo_b,
            )

            tamanho_x = self.calcularTamanhoEixoPerpendicular(
                self.dx,
                cubo_perpendicular,
            )

            self.vara_e_y = cubo_a
            self.vara_b_y = cubo_b

            self.vara_e_x = cubo_perpendicular
            self.vara_b_x = cubo_perpendicular

        # A vara mais curta também fica a uma distância >= L
        # da fronteira inferior, porque o domínio usa a maior vara.
        tamanho_z = (
            max(
                self.comprimento_vara,
                self.comprimento_vara_b,
            )
            + L
        )

        self.definirDimensoesFisicas(
            tamanho_x,
            tamanho_y,
            tamanho_z,
        )

        self.atualizarDistanciaEntreVaras()

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

    def atualizarDistanciaEntreVaras(self):

        if not self.vara_ativa or not self.vara_b_ativa:
            self.distancia_varas = 0.0

            if hasattr(self, "distancia_varas_input"):
                spin = self.distancia_varas_input.spin_box
                spin.blockSignals(True)
                spin.setValue(0.0)
                spin.blockSignals(False)

            return

        centro_a_x = self.centroDoCubo(
            self.vara_e_x,
            self.sx,
            self.dx,
        )

        centro_a_y = self.centroDoCubo(
            self.vara_e_y,
            self.sy,
            self.dy,
        )

        centro_b_x = self.centroDoCubo(
            self.vara_b_x,
            self.sx,
            self.dx,
        )

        centro_b_y = self.centroDoCubo(
            self.vara_b_y,
            self.sy,
            self.dy,
        )

        delta_x = centro_b_x - centro_a_x
        delta_y = centro_b_y - centro_a_y

        distancia_centros = (
            delta_x ** 2 + delta_y ** 2
        ) ** 0.5

        self.distancia_varas = max(
            0.0,
            distancia_centros
            - self.raio_vara
            - self.raio_vara_b,
        )

        if hasattr(self, "distancia_varas_input"):
            spin = self.distancia_varas_input.spin_box

            spin.blockSignals(True)
            spin.setValue(self.distancia_varas)
            spin.blockSignals(False)

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

    def criarObjetoMalha(self):

        # Executa todo o fluxo normal da Page1Vara
        super().criarObjetoMalha()

        # Faz a Vara 2 passar pelo mesmo tipo de atualização
        if hasattr(
                self,
                "comprimento_b_input",
        ):
            self.ajustarParametrosVaraB()

    # ==========================================================
    # DISTÂNCIAS REAIS OBTIDAS
    # ==========================================================

    def obterDistanciasReaisDuasVaras(self):

        if not self.vara_ativa or not self.vara_b_ativa:
            return None

        centro_a_x = self.centroDoCubo(
            self.vara_e_x,
            self.sx,
            self.dx,
        )

        centro_a_y = self.centroDoCubo(
            self.vara_e_y,
            self.sy,
            self.dy,
        )

        centro_b_x = self.centroDoCubo(
            self.vara_b_x,
            self.sx,
            self.dx,
        )

        centro_b_y = self.centroDoCubo(
            self.vara_b_y,
            self.sy,
            self.dy,
        )

        r_a = self.raio_vara
        r_b = self.raio_vara_b

        # Menor distância lateral entre cada superfície cilíndrica
        # e qualquer uma das quatro fronteiras laterais do domínio.
        fronteira_a = min(
            centro_a_x - r_a,
            self.sx - centro_a_x - r_a,
            centro_a_y - r_a,
            self.sy - centro_a_y - r_a,
        )

        fronteira_b = min(
            centro_b_x - r_b,
            self.sx - centro_b_x - r_b,
            centro_b_y - r_b,
            self.sy - centro_b_y - r_b,
        )

        distancia_centros = (
            (centro_b_x - centro_a_x) ** 2
            + (centro_b_y - centro_a_y) ** 2
        ) ** 0.5

        entre_varas = (
            distancia_centros - r_a - r_b
        )

        return (
            fronteira_a,
            entre_varas,
            fronteira_b,
        )

    def avisarPosicionamentoAutomatico(self):

        if not self.geometriaAutomaticaAtiva():
            return

        if not self.vara_ativa or not self.vara_b_ativa:
            self.avisarVaraNaoCentrada()
            return

        distancias = self.obterDistanciasReaisDuasVaras()

        if distancias is None:
            return

        fronteira_a, entre_varas, fronteira_b = distancias

        tolerancia = 1e-6

        # No modo automático a fronteira configurada é um mínimo.
        # Distâncias superiores são válidas.
        if (
            fronteira_a + tolerancia >= self.dist_fronteira
            and fronteira_b + tolerancia >= self.dist_fronteira
        ):
            return

        eixo = getattr(
            self,
            "eixo_varas",
            "X",
        )

        QMessageBox.warning(
            self,
            "Distância à fronteira",
            (
                "A discretização atual não conseguiu garantir "
                "a distância mínima configurada para as duas varas.\n\n"
                f"Eixo utilizado: {eixo}\n\n"
                f"Distância mínima pretendida: "
                f"{self.dist_fronteira:.3f} m\n"
                f"Menor distância da Vara 1 à fronteira: "
                f"{fronteira_a:.3f} m\n"
                f"Menor distância da Vara 2 à fronteira: "
                f"{fronteira_b:.3f} m\n"
                f"Distância calculada entre as varas: "
                f"{entre_varas:.3f} m"
            ),
        )

    def obterEixoAutomaticoDuasVaras(self):

        x_valido = self.dx >= 2
        y_valido = self.dy >= 2

        if not x_valido and not y_valido:
            raise ValueError(
                "Para colocar duas varas são necessárias "
                "pelo menos 2 divisões em X ou em Y."
            )

        if x_valido and not y_valido:
            return "X"

        if y_valido and not x_valido:
            return "Y"

        x_impar = self.dx % 2 != 0
        y_impar = self.dy % 2 != 0

        # Se apenas um dos eixos é ímpar, ele tem prioridade,
        # mesmo que o outro tenha mais divisões.
        if x_impar and not y_impar:
            return "X"

        if y_impar and not x_impar:
            return "Y"

        # Se os dois têm a mesma paridade, usa o eixo com mais
        # divisões. Em empate, X.
        if self.dx >= self.dy:
            return "X"

        return "Y"

    def updateVaraAtiva(
        self,
        checked,
    ):

        self.vara_ativa = checked
        self.vara_toggle.setText(
            "ON" if checked else "OFF"
        )

        self.vara_config.setVisible(checked)
        self.atualizarEstadoAutomatico()

        if self.geometriaAutomaticaAtiva():
            self.atualizarGeometriaAutomatica()
        else:
            self.gerarMalhaNormal()

    def updateRaio(
        self,
        value,
    ):

        self.raio_vara = value

        if self.geometriaAutomaticaAtiva():
            self.atualizarGeometriaAutomatica()
        else:
            self.atualizarDistanciaEntreVaras()

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

    def updateVaraX(
        self,
        value,
    ):

        self.vara_e_x = value
        self.atualizarDistanciaEntreVaras()

    def updateVaraY(
        self,
        value,
    ):

        self.vara_e_y = value
        self.atualizarDistanciaEntreVaras()

    def updateVaraBAtiva(
        self,
        checked,
    ):

        self.vara_b_ativa = checked
        self.vara_b_toggle.setText(
            "ON" if checked else "OFF"
        )

        self.vara_b_config.setVisible(checked)
        self.atualizarEstadoAutomatico()

        if self.geometriaAutomaticaAtiva():
            self.atualizarGeometriaAutomatica()
        else:
            self.atualizarDistanciaEntreVaras()
            self.gerarMalhaNormal()

    def updateVaraBX(
        self,
        value,
    ):

        self.vara_b_x = value
        self.atualizarDistanciaEntreVaras()

    def updateVaraBY(
        self,
        value,
    ):

        self.vara_b_y = value
        self.atualizarDistanciaEntreVaras()

    def updateRaioB(
        self,
        value,
    ):

        self.raio_vara_b = value

        if self.geometriaAutomaticaAtiva():
            self.atualizarGeometriaAutomatica()
        else:
            self.atualizarDistanciaEntreVaras()

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
        # Campo apenas informativo. O valor é atualizado por
        # atualizarDistanciaEntreVaras().
        pass

    def updateAvancado(
        self,
        checked,
    ):

        self.avancado_ativo = checked
        self.avancado_container.setVisible(checked)

        self.atualizarEstadoAutomatico()

        if self.geometriaAutomaticaAtiva():
            self.atualizarGeometriaAutomatica()
        else:
            self.gerarMalhaNormal()

    def updateAvancadoB(
        self,
        checked,
    ):

        self.avancado_b_ativo = checked
        self.avancado_b_container.setVisible(checked)

        self.atualizarEstadoAutomatico()

        if self.geometriaAutomaticaAtiva():
            self.atualizarGeometriaAutomatica()
        else:
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

        if not self.vara_ativa and not self.vara_b_ativa:
            self.gerarMalhaNormal()
            return

        if (
            self.vara_ativa
            and self.avancado_ativo
            and self.max_div is not None
            and self.max_div < self.min_div
        ):
            QMessageBox.warning(
                self,
                "Configuração inválida",
                "Na Vara 1, Máx. divisões não pode ser "
                "inferior a Mín. divisões.",
            )
            return

        if (
            self.vara_b_ativa
            and self.avancado_b_ativo
            and self.max_div_b is not None
            and self.max_div_b < self.min_div_b
        ):
            QMessageBox.warning(
                self,
                "Configuração inválida",
                "Na Vara 2, Máx. divisões não pode ser "
                "inferior a Mín. divisões.",
            )
            return

        # Antes do BUILD, recalcula a geometria e a distância
        # resultante entre as varas. Assim o objeto Malha é criado
        # já com os tamanhos físicos definitivos.
        if self.geometriaAutomaticaAtiva():
            if not self.atualizarGeometriaAutomatica(
                gerar_malha=False,
                mostrar_erro=True,
            ):
                return

        if not self.geometriaAutomaticaAtiva():
            self.atualizarDistanciaEntreVaras()

        estratos = self.lerEstratos()

        if estratos is None:
            return

        self.estratos = estratos
        self.resistividades_estratos = (
            self.obterResistividadesEstratos()
        )

        self.criarObjetoMalha()

        try:

            if self.vara_ativa and self.vara_b_ativa:
                self.gerarDuasVaras()

            elif self.vara_ativa:
                self.gerarApenasVara1()

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
            self.vara_e_x = self.dx - 1

        self.vara_x_spin.spin_box.setMaximum(
            self.dx - 1
        )
        self.vara_x_spin.spin_box.setValue(
            self.vara_e_x
        )

        if hasattr(self, "vara_b_x_input"):

            if self.vara_b_x >= self.dx:
                self.vara_b_x = self.dx - 1

            self.vara_b_x_input.spin_box.setMaximum(
                self.dx - 1
            )
            self.vara_b_x_input.spin_box.setValue(
                self.vara_b_x
            )

        if self.geometriaAutomaticaAtiva():
            self.atualizarGeometriaAutomatica()
        else:
            self.gerarMalhaNormal()

    def updateDy(
        self,
        value,
    ):

        self.dy = value

        if self.vara_e_y >= self.dy:
            self.vara_e_y = self.dy - 1

        self.vara_y_spin.spin_box.setMaximum(
            self.dy - 1
        )
        self.vara_y_spin.spin_box.setValue(
            self.vara_e_y
        )

        if hasattr(self, "vara_b_y_input"):

            if self.vara_b_y >= self.dy:
                self.vara_b_y = self.dy - 1

            self.vara_b_y_input.spin_box.setMaximum(
                self.dy - 1
            )
            self.vara_b_y_input.spin_box.setValue(
                self.vara_b_y
            )

        if self.geometriaAutomaticaAtiva():
            self.atualizarGeometriaAutomatica()
        else:
            self.gerarMalhaNormal()

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
            except ValueError as erro:
                QMessageBox.warning(
                    self,
                    "Configuração das varas",
                    str(erro),
                )

        self.atualizarDistanciaEntreVaras()
        self.gerarMalhaNormal()

        if hasattr(self, "raio_b_input"):
            self.ajustarParametrosVaraB()

    def updateSy(
        self,
        value,
    ):

        self.sy = value

        if self.geometriaAutomaticaAtiva():
            try:
                self.atualizarPosicoesAutomaticas()
            except ValueError as erro:
                QMessageBox.warning(
                    self,
                    "Configuração das varas",
                    str(erro),
                )

        self.atualizarDistanciaEntreVaras()
        self.gerarMalhaNormal()

        if hasattr(self, "raio_b_input"):
            self.ajustarParametrosVaraB()

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
