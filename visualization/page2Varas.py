import numpy as np
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

        # Vara 2
        self.vara_b_ativa = False
        self.vara_b_x = 0
        self.vara_b_y = 0
        self.raio_vara_b = 0.00794
        self.comprimento_vara_b = 1.0

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

        self.moverBotaoBuild()


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

        labels = self.findChildren(QLabel)

        for label in labels:

            if label.text() == "Setup Vara":

                label.setText(
                    "Setup Vara 1"
                )

                break


    def adicionarSetupVara2(self):

        parent = self.vara_config.parentWidget()

        parent_layout = parent.layout()

        indice_vara_1 = parent_layout.indexOf(
            self.vara_config
        )

        indice_vara_2 = indice_vara_1 + 1

        # Bloco completo da Vara 2
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
        # CONFIGURAÇÃO DA VARA 2
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

        # Posição
        config_layout.addWidget(
            QLabel("Posição da Vara 2")
        )

        self.vara_b_x_input = (
            self.createLabeledIntegerInput(
                "Eixo X",
                0,
                self.dx - 1,
                self.vara_b_x,
                self.updateVaraBX,
            )
        )

        self.vara_b_y_input = (
            self.createLabeledIntegerInput(
                "Eixo Y",
                0,
                self.dy - 1,
                self.vara_b_y,
                self.updateVaraBY,
            )
        )

        config_layout.addWidget(
            self.vara_b_x_input
        )

        config_layout.addWidget(
            self.vara_b_y_input
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

        # Raio
        raio_maximo = self._raioMaximo(
            self.sx,
            self.sy,
        )

        self.raio_b_input = (
            self.createPreciseFloatInput(
                "Raio",
                0.00001,
                raio_maximo,
                self.raio_vara_b,
                self.updateRaioB,
                5,
            )
        )

        config_layout.addWidget(
            self.raio_b_input
        )

        self.vara_b_config.setVisible(
            False
        )

        bloco_layout.addWidget(
            self.vara_b_config
        )

        parent_layout.insertWidget(
            indice_vara_2,
            self.vara_b_bloco,
        )


    def moverBotaoBuild(self):

        build_button = None

        layout_vara_1 = self.vara_config.layout()

        # Procura o BUILD que veio da Page1Vara
        for i in range(
            layout_vara_1.count()
        ):

            item = layout_vara_1.itemAt(i)

            widget = item.widget()

            if not isinstance(
                widget,
                QPushButton,
            ):
                continue

            if widget.text() == "BUILD":

                build_button = widget
                break

        if build_button is None:
            return

        # Retira o BUILD do Setup Vara 1
        layout_vara_1.removeWidget(
            build_button
        )

        # Coloca depois do Setup Vara 2
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

        self.build_button = build_button


    # ==========================================================
    # ALTERAÇÃO DOS PARÂMETROS DA VARA 2
    #
    # Estas funções apenas alteram valores.
    # Não geram malha.
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

        # Ao ligar/desligar uma vara volta à malha normal.
        # A malha com varas só aparece quando se carrega BUILD.
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


    def updateComprimentoB(
        self,
        value,
    ):

        self.comprimento_vara_b = value


    # ==========================================================
    # LIMITES DA VARA 2
    # ==========================================================

    def ajustarParametrosVaraB(self):

        tamanho_x, tamanho_y, tamanho_z = (
            self.obterTamanhosDaMalha()
        )

        raio_maximo = self._raioMaximo(
            tamanho_x,
            tamanho_y,
        )

        if self.raio_vara_b > raio_maximo:

            self.raio_vara_b = raio_maximo

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

            self.comprimento_vara_b = tamanho_z

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

        # Nenhuma vara selecionada
        if (
            not self.vara_ativa
            and not self.vara_b_ativa
        ):

            self.gerarMalhaNormal()

            return

        # Lê os estratos
        estratos = self.lerEstratos()

        if estratos is None:
            return

        self.estratos = estratos

        self.resistividades_estratos = (
            self.obterResistividadesEstratos()
        )

        # Cria uma nova Malha com os valores atuais
        self.criarObjetoMalha()

        # Corrige limites da Vara 2
        self.ajustarParametrosVaraB()

        try:

            # ==================================================
            # DUAS VARAS
            # ==================================================

            if (
                self.vara_ativa
                and self.vara_b_ativa
            ):

                self.gerarDuasVaras()

            # ==================================================
            # APENAS VARA 1
            # ==================================================

            elif self.vara_ativa:

                self.gerarApenasVara1()

            # ==================================================
            # APENAS VARA 2
            # ==================================================

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


    # ==========================================================
    # GERAR VARA 1
    # ==========================================================

    def gerarApenasVara1(self):

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

        self.guardarMalhaGerada(
            pontos,
            cubos,
            normais,
            deformados,
        )

        self.numero_varas_construidas = 1


    # ==========================================================
    # GERAR VARA 2
    # ==========================================================

    def gerarApenasVara2(self):

        pontos, cubos, normais, deformados = (
            self.malha.gerarMalha1Vara(
                self.vara_b_x,
                self.vara_b_y,
                self.raio_vara_b,
                self.comprimento_vara_b,
                automatico=True,
                estrato=self.estratos,
                distVara=self.dist_fronteira,
            )
        )

        self.guardarMalhaGerada(
            pontos,
            cubos,
            normais,
            deformados,
        )

        self.numero_varas_construidas = 1


    # ==========================================================
    # GERAR DUAS VARAS
    # ==========================================================

    def gerarDuasVaras(self):

        mesma_posicao = (
            self.vara_e_x == self.vara_b_x
            and self.vara_e_y == self.vara_b_y
        )

        if mesma_posicao:

            self.gerarVarasNaMesmaPosicao()

            return

        pontos, cubos, normais, deformados_a, deformados_b = (
            self.malha.gerarMalha2Vara(
                self.vara_e_x,
                self.vara_e_y,
                self.raio_vara,
                self.comprimento_vara,

                None,
                1,
                None,
                1.55,

                self.vara_b_x,
                self.vara_b_y,
                self.raio_vara_b,
                self.comprimento_vara_b,

                None,
                1,
                None,
                1.55,

                automatico=True,
                estrato=self.estratos,
                distVara=self.dist_fronteira,
            )
        )

        deformados = (
            list(deformados_a)
            + list(deformados_b)
        )

        self.guardarMalhaGerada(
            pontos,
            cubos,
            normais,
            deformados,
        )

        self.numero_varas_construidas = 2


    # ==========================================================
    # DUAS VARAS NA MESMA POSIÇÃO
    # ==========================================================

    def gerarVarasNaMesmaPosicao(self):

        raio_medio = (
            self.raio_vara
            + self.raio_vara_b
        ) / 2

        comprimento_medio = (
            self.comprimento_vara
            + self.comprimento_vara_b
        ) / 2

        pontos, cubos, normais, deformados = (
            self.malha.gerarMalha1Vara(
                self.vara_e_x,
                self.vara_e_y,
                raio_medio,
                comprimento_medio,
                automatico=True,
                estrato=self.estratos,
                distVara=self.dist_fronteira,
            )
        )

        self.guardarMalhaGerada(
            pontos,
            cubos,
            normais,
            deformados,
        )

        self.numero_varas_construidas = 1


    # ==========================================================
    # GUARDAR RESULTADO DO BUILDER
    # ==========================================================

    def guardarMalhaGerada(
        self,
        pontos,
        cubos,
        normais,
        deformados,
    ):

        self.malha.points_list = pontos
        self.malha.cube_list = cubos

        self.malha.final_points_list = pontos
        self.malha.final_cube_list = cubos

        self.cubos_normais = normais
        self.cubos_deformados = deformados


    def guardarParametrosDaConstrucao(self):

        dados = {
            "estratos": self.estratos.copy(),
            "resistividades": (
                self.resistividades_estratos.copy()
            ),
            "dist_fronteira": self.dist_fronteira,
        }

        if self.vara_ativa:

            dados["vara_1"] = {
                "x": self.vara_e_x,
                "y": self.vara_e_y,
                "raio": self.raio_vara,
                "comprimento": self.comprimento_vara,
            }

        if self.vara_b_ativa:

            dados["vara_2"] = {
                "x": self.vara_b_x,
                "y": self.vara_b_y,
                "raio": self.raio_vara_b,
                "comprimento": self.comprimento_vara_b,
            }

        self.parametros_varas_construidas = dados


    # ==========================================================
    # MALHA NORMAL
    # ==========================================================

    def gerarMalhaNormal(self):

        super().gerarMalhaNormal()

        self.numero_varas_construidas = 0

        self.parametros_varas_construidas = None


    # ==========================================================
    # ALTERAÇÃO DAS DIVISÕES
    # ==========================================================

    def updateDx(
        self,
        value,
    ):

        # Atualiza primeiro a Vara 2
        if hasattr(
            self,
            "vara_b_x_input",
        ):

            if self.vara_b_x >= value:

                self.vara_b_x = value - 1

            spin_box = (
                self.vara_b_x_input.spin_box
            )

            spin_box.blockSignals(
                True
            )

            spin_box.setMaximum(
                value - 1
            )

            spin_box.setValue(
                self.vara_b_x
            )

            spin_box.blockSignals(
                False
            )

        # Page1Vara atualiza a Vara 1
        # e gera a malha normal.
        super().updateDx(
            value
        )


    def updateDy(
        self,
        value,
    ):

        if hasattr(
            self,
            "vara_b_y_input",
        ):

            if self.vara_b_y >= value:

                self.vara_b_y = value - 1

            spin_box = (
                self.vara_b_y_input.spin_box
            )

            spin_box.blockSignals(
                True
            )

            spin_box.setMaximum(
                value - 1
            )

            spin_box.setValue(
                self.vara_b_y
            )

            spin_box.blockSignals(
                False
            )

        super().updateDy(
            value
        )


    # ==========================================================
    # ALTERAÇÃO DAS DIMENSÕES
    # ==========================================================

    def updateSx(
        self,
        value,
    ):

        super().updateSx(
            value
        )

        if hasattr(
            self,
            "raio_b_input",
        ):
            self.ajustarParametrosVaraB()


    def updateSy(
        self,
        value,
    ):

        super().updateSy(
            value
        )

        if hasattr(
            self,
            "raio_b_input",
        ):
            self.ajustarParametrosVaraB()


    def updateSz(
        self,
        value,
    ):

        super().updateSz(
            value
        )

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

        else:

            vetor = (
                self.malha.getVetorList()
            )

        # ==========================================================
        # TIPO DA MALHA
        # ==========================================================

        if self.numero_varas_construidas == 2:

            tipo_malha = "2Varas"

        elif self.numero_varas_construidas == 1:

            tipo_malha = "1Vara"

        else:

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
            v=1000000,
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