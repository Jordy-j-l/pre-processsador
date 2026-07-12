from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox

from mesh.Builder import Malha
from visualization.page1Vara import Page1Vara


class Page2Varas(Page1Vara):
    """Pagina que permite ativar e configurar duas varas independentes."""

    def __init__(self, voltar):
        self.vara_b_ativa = False
        self.vara_b_x = 0
        self.vara_b_y = 0
        self.raio_vara_b = 0.00794
        self.comprimento_vara_b = 1.0
        self.camadas_b = 6
        self.max_div_b = 4
        self.min_div_b = 1
        self.ballooning_b = 1.55
        super().__init__(voltar)
        self._adicionarSetupVaraB()
        for label in self.findChildren(QLabel):
            if label.text() == "Setup Vara":
                label.setText("Setup Vara 1")
                break
        titulo = self.findChild(QLabel, "panelTitle")
        if titulo is not None:
            titulo.setText("Malha com duas Varas")

    def _adicionarSetupVaraB(self):
        parent_layout = self.vara_config.parentWidget().layout()
        indice = parent_layout.indexOf(self.vara_config) + 1

        bloco = QWidget()
        layout = QVBoxLayout(bloco)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(10)

        cabecalho = QWidget()
        cabecalho_layout = QHBoxLayout(cabecalho)
        cabecalho_layout.setContentsMargins(0, 0, 0, 0)
        titulo = QLabel("Setup Vara 2")
        titulo.setObjectName("sectionTitle")
        self.vara_b_toggle = QCheckBox("OFF")
        self.vara_b_toggle.toggled.connect(self.updateVaraBAtiva)
        cabecalho_layout.addWidget(titulo)
        cabecalho_layout.addWidget(self.vara_b_toggle)
        layout.addWidget(cabecalho)

        self.vara_b_config = QWidget()
        config = QVBoxLayout(self.vara_b_config)
        config.setContentsMargins(0, 0, 0, 0)
        config.setSpacing(10)
        config.addWidget(QLabel("Posição da Vara 2"))
        self.vara_b_x_input = self.createLabeledIntegerInput(
            "Eixo X", 0, self.dx - 1, self.vara_b_x, self.updateVaraBX)
        self.vara_b_y_input = self.createLabeledIntegerInput(
            "Eixo Y", 0, self.dy - 1, self.vara_b_y, self.updateVaraBY)
        config.addWidget(self.vara_b_x_input)
        config.addWidget(self.vara_b_y_input)
        config.addWidget(self.createPreciseFloatInput(
            "Raio", 0.00001, min(self.dx/self.sx,self.dy/self.sy)/2, self.raio_vara_b, self.updateRaioB, 5))
        self.comprimento_b_input = self.createPreciseFloatInput(
            "Comprimento", 0.1, self.sz, self.comprimento_vara_b,
            self.updateComprimentoB, 2)
        config.addWidget(self.comprimento_b_input)
        config.addWidget(self.createLabeledIntegerInput(
            "Camadas deformadas", 1, 20, self.camadas_b, self.updateCamadasB))
        self.max_div_b_input = self.createLabeledIntegerInput(
            "Máximo de divisões", self.min_div_b, 20, self.max_div_b, self.updateMaxDivB)
        self.min_div_b_input = self.createLabeledIntegerInput(
            "Mínimo de divisões", 1, self.max_div_b, self.min_div_b, self.updateMinDivB)
        config.addWidget(self.max_div_b_input)
        config.addWidget(self.min_div_b_input)
        config.addWidget(self.createPreciseFloatInput(
            "Razão ballooning", 1.0, 10.0, self.ballooning_b,
            self.updateBallooningB, 2))
        self.vara_b_config.setVisible(False)
        layout.addWidget(self.vara_b_config)
        parent_layout.insertWidget(indice, bloco)

    def configuracaoA(self):
        return dict(x=self.vara_e_x, y=self.vara_e_y, raio=self.raio_vara,
                    comprimento=self.comprimento_vara, max_div=self.max_div,
                    min_div=self.min_div, camadas=self.camadas_deformadas,
                    ballooning=self.ballooning)

    def configuracaoB(self):
        return dict(x=self.vara_b_x, y=self.vara_b_y, raio=self.raio_vara_b,
                    comprimento=self.comprimento_vara_b, max_div=self.max_div_b,
                    min_div=self.min_div_b, camadas=self.camadas_b,
                    ballooning=self.ballooning_b)

    def updateMalha(self, sxf, syf, szf):
        self.malha = Malha(self.dx, self.dy, self.dz, sxf, syf, szf)
        self.cubos_normais = None
        self.cubos_deformados = None
        if self.vara_ativa and self.vara_b_ativa:
            vara_a = self.configuracaoA()
            vara_b = self.configuracaoB()

            mesma_posicao = (
                vara_a["x"] == vara_b["x"]
                and vara_a["y"] == vara_b["y"]
            )

            if mesma_posicao:
                raio = (vara_a["raio"] + vara_b["raio"]) / 2
                comprimento = (vara_a["comprimento"] + vara_b["comprimento"]) / 2
                max_div = round((vara_a["max_div"] + vara_b["max_div"]) / 2)
                min_div = round((vara_a["min_div"] + vara_b["min_div"]) / 2)
                camadas = round((vara_a["camadas"] + vara_b["camadas"]) / 2)
                ballooning = (vara_a["ballooning"] + vara_b["ballooning"]) / 2

                pontos, cubos, normais, deformados = self.malha.gerarMalha1Vara(
                    vara_a["x"], vara_a["y"], raio, comprimento,
                    max_div, min_div, camadas, ballooning,
                )
            else:
                pontos, cubos, normais, deform_a, deform_b = self.malha.gerarMalha2Vara(
                    vara_a["x"], vara_a["y"], vara_a["raio"],
                    vara_a["comprimento"], vara_a["max_div"], vara_a["min_div"],
                    vara_a["camadas"], vara_a["ballooning"],
                    vara_b["x"], vara_b["y"], vara_b["raio"],
                    vara_b["comprimento"], vara_b["max_div"], vara_b["min_div"],
                    vara_b["camadas"], vara_b["ballooning"],
                )
                deformados = list(deform_a) + list(deform_b)
        elif self.vara_ativa:
            cfg = self.configuracaoA()
            pontos, cubos, normais, deformados = self.malha.gerarMalha1Vara(
                cfg["x"], cfg["y"], cfg["raio"], cfg["comprimento"],
                cfg["max_div"], cfg["min_div"], cfg["camadas"], cfg["ballooning"])
        elif self.vara_b_ativa:
            cfg = self.configuracaoB()
            pontos, cubos, normais, deformados = self.malha.gerarMalha1Vara(
                cfg["x"], cfg["y"], cfg["raio"], cfg["comprimento"],
                cfg["max_div"], cfg["min_div"], cfg["camadas"], cfg["ballooning"])
        else:
            return

        self.malha.points_list = pontos
        self.malha.cube_list = cubos
        self.malha.final_points_list = pontos
        self.malha.final_cube_list = cubos
        self.cubos_normais = normais
        self.cubos_deformados = deformados

    def updateVaraAtiva(self, checked):
        self.vara_ativa = checked
        self.vara_toggle.setText("ON" if checked else "OFF")
        self.vara_config.setVisible(checked)
        self.updateAll()

    def updateVaraBAtiva(self, checked):
        self.vara_b_ativa = checked
        self.vara_b_toggle.setText("ON" if checked else "OFF")
        self.vara_b_config.setVisible(checked)
        self.updateAll()

    def _atualizarB(self):
        self.updateAll()

    def updateVaraBX(self, value): self.vara_b_x = value; self._atualizarB()
    def updateVaraBY(self, value): self.vara_b_y = value; self._atualizarB()
    def updateRaioB(self, value): self.raio_vara_b = value; self._atualizarB()
    def updateComprimentoB(self, value): self.comprimento_vara_b = value; self._atualizarB()
    def updateCamadasB(self, value): self.camadas_b = value; self._atualizarB()
    def updateBallooningB(self, value): self.ballooning_b = value; self._atualizarB()

    def updateMaxDivB(self, value):
        self.max_div_b = value
        self.min_div_b_input.spin_box.setMaximum(value)
        self._atualizarB()

    def updateMinDivB(self, value):
        self.min_div_b = value
        self.max_div_b_input.spin_box.setMinimum(value)
        self._atualizarB()

    def updateDx(self, value):
        if hasattr(self, "vara_b_x_input"):
            self.vara_b_x = min(self.vara_b_x, value - 1)
            self.vara_b_x_input.spin_box.blockSignals(True)
            self.vara_b_x_input.spin_box.setMaximum(value - 1)
            self.vara_b_x_input.spin_box.setValue(self.vara_b_x)
            self.vara_b_x_input.spin_box.blockSignals(False)
        super().updateDx(value)

    def updateDy(self, value):
        if hasattr(self, "vara_b_y_input"):
            self.vara_b_y = min(self.vara_b_y, value - 1)
            self.vara_b_y_input.spin_box.blockSignals(True)
            self.vara_b_y_input.spin_box.setMaximum(value - 1)
            self.vara_b_y_input.spin_box.setValue(self.vara_b_y)
            self.vara_b_y_input.spin_box.blockSignals(False)
        super().updateDy(value)

    def updateSz(self, value):
        if hasattr(self, "comprimento_b_input"):
            self.comprimento_b_input.spin_box.setMaximum(value)

            if self.comprimento_vara_b > value:
                self.comprimento_vara_b = value
                self.comprimento_b_input.spin_box.setValue(value)

        super().updateSz(value)
