import numpy as np
from pathlib import Path


class Export:

    def __init__(
        self,
        element_list,
        point_list,
        vector_list,
        estratos=None,
        resistividades=None,
        rho=100,
        v=1000000,
    ):

        self.element_list = np.asarray(
            element_list
        )

        self.point_list = np.asarray(
            point_list,
            dtype=float,
        )

        self.vector_list = np.asarray(
            vector_list
        )

        self.rho = rho
        self.v = v

        if estratos is None:
            estratos = []

        if resistividades is None:
            resistividades = []

        self.estratos = list(
            estratos
        )

        self.resistividades = list(
            resistividades
        )

        self.pasta = Path(
            "output/downloads"
        )

        self.pasta.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.validarEstratos()


    # ==========================================================
    # ESTRATOS
    # ==========================================================

    def validarEstratos(self):

        if len(self.estratos) != len(
            self.resistividades
        ):

            raise ValueError(
                "O número de estratos deve ser igual "
                "ao número de resistividades."
            )

        pares = []

        for i in range(
            len(self.estratos)
        ):

            profundidade = float(
                self.estratos[i]
            )

            resistividade = float(
                self.resistividades[i]
            )

            pares.append(
                (
                    profundidade,
                    resistividade,
                )
            )

        pares.sort(
            key=lambda par: par[0]
        )

        self.estratos = []
        self.resistividades = []

        for profundidade, resistividade in pares:

            self.estratos.append(
                profundidade
            )

            self.resistividades.append(
                resistividade
            )


    # ==========================================================
    # ELEMENTOS
    # ==========================================================

    def obterNosDosElementos(self):

        if self.element_list.ndim != 2:

            raise ValueError(
                "A lista de elementos deve ser uma matriz."
            )

        numero_colunas = (
            self.element_list.shape[1]
        )

        # Formato interno da malha:
        #
        # [4, no1, no2, no3, no4]
        if numero_colunas == 5:

            primeira_coluna = (
                self.element_list[:, 0]
            )

            if np.all(
                primeira_coluna == 4
            ):

                return self.element_list[
                    :,
                    1:5,
                ].astype(int)

        # Formato já limpo:
        #
        # [no1, no2, no3, no4]
        if numero_colunas == 4:

            return self.element_list.astype(
                int
            )

        raise ValueError(
            "Formato dos elementos inválido."
        )


    def calcularCentroDoElemento(
        self,
        nos,
    ):

        pontos_elemento = (
            self.point_list[nos]
        )

        centro = np.mean(
            pontos_elemento,
            axis=0,
        )

        return centro


    def calcularProfundidadeElemento(
        self,
        nos,
    ):

        centro = (
            self.calcularCentroDoElemento(
                nos
            )
        )

        z_centro = centro[2]

        altura_dominio = np.max(
            self.point_list[:, 2]
        )

        profundidade = (
            altura_dominio
            - z_centro
        )

        return profundidade


    def obterResistividade(
        self,
        profundidade,
    ):

        # Solo homogéneo
        if len(self.estratos) == 0:

            return self.rho

        # Procura o estrato onde está o elemento
        for i in range(
            len(self.estratos)
        ):

            limite = (
                self.estratos[i]
            )

            if profundidade <= limite:

                return (
                    self.resistividades[i]
                )

        # Se estiver abaixo do último limite,
        # mantém a resistividade do último estrato.
        return self.resistividades[-1]


    def prepararElementos(self):

        nos_elementos = (
            self.obterNosDosElementos()
        )

        elementos_export = np.empty(
            (
                len(nos_elementos),
                5,
            ),
            dtype=float,
        )

        for i in range(
            len(nos_elementos)
        ):

            nos = nos_elementos[i]

            profundidade = (
                self.calcularProfundidadeElemento(
                    nos
                )
            )

            resistividade = (
                self.obterResistividade(
                    profundidade
                )
            )

            elementos_export[i, 0] = nos[0]
            elementos_export[i, 1] = nos[1]
            elementos_export[i, 2] = nos[2]
            elementos_export[i, 3] = nos[3]

            elementos_export[i, 4] = (
                resistividade
            )

        return elementos_export


    # ==========================================================
    # PONTOS
    # ==========================================================

    def prepararPontos(self):

        pontos_export = np.empty(
            (
                len(self.point_list),
                4,
            ),
            dtype=float,
        )

        quantidade_zero = int(
            self.vector_list[0]
        )

        quantidade_tensao = int(
            self.vector_list[1]
        )

        fim_tensao = (
            quantidade_zero
            + quantidade_tensao
        )

        for i in range(
            len(self.point_list)
        ):

            pontos_export[i, 0] = (
                self.point_list[i][0]
            )

            pontos_export[i, 1] = (
                self.point_list[i][1]
            )

            pontos_export[i, 2] = (
                self.point_list[i][2]
            )

            if i < quantidade_zero:

                pontos_export[i, 3] = -1

            elif i < fim_tensao:

                pontos_export[i, 3] = (
                    self.v
                )

            else:

                pontos_export[i, 3] = 0

        return pontos_export


    # ==========================================================
    # EXPORTAÇÃO
    # ==========================================================

    def exportPointList(
        self,
        name="pontos",
    ):

        pontos = (
            self.prepararPontos()
        )

        caminho = (
            self.pasta
            / f"{name}.txt"
        )

        np.savetxt(
            caminho,
            pontos,
            fmt="%.6f",
        )

        return caminho


    def exportElementList(
        self,
        name="elementos",
    ):

        elementos = (
            self.prepararElementos()
        )

        caminho = (
            self.pasta
            / f"{name}.txt"
        )

        np.savetxt(
            caminho,
            elementos,
            fmt=[
                "%d",
                "%d",
                "%d",
                "%d",
                "%.6f",
            ],
        )

        return caminho


    def exportVector(
        self,
        name="Vetor",
    ):

        caminho = (
            self.pasta
            / f"{name}.txt"
        )

        np.savetxt(
            caminho,
            self.vector_list,
            fmt="%d",
        )

        return caminho


    def exportAll(
        self,
        name_e="elementos",
        name_p="pontos",
        name_v="Vetor",
    ):

        caminho_elementos = (
            self.exportElementList(
                name_e
            )
        )

        caminho_pontos = (
            self.exportPointList(
                name_p
            )
        )

        caminho_vetor = (
            self.exportVector(
                name_v
            )
        )

        return (
            caminho_elementos,
            caminho_pontos,
            caminho_vetor,
        )