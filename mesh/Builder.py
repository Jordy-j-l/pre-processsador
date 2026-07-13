import numpy as np

class Malha:

    def __init__(self, dx, dy, dz,sx=None,sy=None,sz=None):
        """Inicializa a malha base.

        Args: dx, dy, dz: divisoes dos eixos; sx, sy, sz: tamanhos fisicos opcionais.
        Returns: None.
        """

        self.dx = dx #quantas vezes dividiR o eixo x
        self.dy = dy #quantas vezes dividir o eixo y
        self.dz = dz #quantas vezes dividir o eixo z
        # ====================================================================
        if sx is None:
            self.sx = dx  # tamanho total do eixo x padronizado
        else:
            self.sx = sx  # tamanho total do eixo x em metros
        # ====================================================================
        if sy is None:
           self.sy = dy # tamanho total do eixoy padronizado
        else:
            self.sy = sy
        # ====================================================================
        if sz is None:
            self.sz = dz # tamanho total do eixo z padronizado
        else:
            self.sz=sz

        #=======================================================================
        #Variaveis para uma vara

        self.raio_vara = 0.00794
        self.comprimento_vara = 3.3
        self.casas_arredondamento = 12
        self.balloning = 1.55
        self.camadas_deformadas=6#em quantas camadas dividiras o cubo para aplicar a deformação de forma suave
        self.varas_ativas = []

        #=======================================================================
        """self.points_list = self.gerarPointsOrdenados()
        self.cube_list=self.gerarCubos()
        self.final_cube_list,self.final_points_list=self.reorganizar()
        self.final_vector=self.gerarVetor()
        return self.final_tetraedro_list"""
    # =======================================================================#
    #=====================Pontos/Indice======================================#
    # =======================================================================#


    def indicePonto(self,ix, iy, iz, quantidade_pontos_y, quantidade_pontos_z):
        """Converte (ix, iy, iz) num indice linear.

        Args: ix, iy, iz: indices 3D; quantidade_pontos_y/z: dimensoes da grelha.
        Returns: Indice inteiro do ponto.
        """
        return iz + iy * quantidade_pontos_z + ix * quantidade_pontos_z * quantidade_pontos_y

    def chavePonto(self,cordenada):
        """Cria uma chave estavel para uma coordenada.

        Args: cordenada: sequencia (x, y, z).
        Returns: Tupla arredondada utilizavel como chave.
        """
        return tuple(np.round(cordenada, self.casas_arredondamento))


    def gerarMapaPontos(self,pontos):
        """Mapeia coordenadas para indices.

        Args: pontos: colecao de coordenadas.
        Returns: Dicionario {coordenada: indice}.
        """
        mapa = {}
        for i, ponto in enumerate(pontos):
            mapa[self.chavePonto(ponto)] = i
        return mapa

    # =======================================================================
    #======================Geração de Pontos=================================
    # =======================================================================
    def gerarPointsOrdenados(self,xv=None,yv=None,zv=None):
        """Gera pontos ordenados com Z como eixo de variacao mais rapida.

        Args: xv, yv, zv: coordenadas opcionais dos eixos; sem elas usa a grelha base.
        Returns: Array NumPy (n, 3) de pontos.
        """

        # tamanho de cada espaçamento entre as divizoes feita
        ex = self.sx / self.dx
        ey = self.sy / self.dy
        ez = self.sz / self.dz



        i = 0
        if xv is not None and yv is not None and zv is not None:
            points = np.empty((len(xv) * len(yv) * len(zv), 3), dtype=float)
            for x in xv:
                for y in yv:
                    for z in zv:
                        points[i] = (x, y, z)
                        i += 1
        else:
            points = np.empty(((self.dx + 1) * (self.dy + 1) * (self.dz + 1), 3))
            for x in range(self.dx + 1):
                for y in range(self.dy + 1):
                    for z in range(self.dz + 1):
                        points[i] = (x * ex, y * ey, z * ez)
                        i += 1
        return points



    def gerarCoordenadasPorEixo(self,numero_cubos, tamanho_cubo, divisoes_por_cubo, origem=0.0):
        """
        Cria as coordenadas de um eixo.

        Cada eixo pode ter uma quantidade diferente de divisoes. Exemplo:
            numero_cubos = dx/dy/dz representando o numero de divizões em um eixo
            tamanho_cubo = sx/sy/sz represnta o size de cada eixo
            divisoes_por_cubo = [1, 4, 1]#é um array com as respetivas divisões neste eixo dado atravez de uma função que aplica o baluning

        Resultado:
        Os cubos perto da vara ficam mais divididos do que os loonge da vara.
        """
        cordenadas = [origem] #a cordenada vai começar em origem do eixo
        intervalos = []

        for cubo in range(numero_cubos):
            inicio = origem + cubo * tamanho_cubo
            divisoes = int(divisoes_por_cubo[cubo])
            indice_inicio = len(cordenadas) - 1 #o inicio da cordenada do cubo principal

            for divisao in range(1, divisoes + 1):
                cordenadas.append(inicio + divisao * tamanho_cubo / divisoes)

            indice_fim = len(cordenadas) - 1#o fim da cordenada do cubo principal
            intervalos.append((indice_inicio, indice_fim))

        return np.asarray(cordenadas, dtype=float), intervalos


    def gerarPontosDoQuadrado(self,x_min, x_max, y_min, y_max, divisoes):
        """Gera os pontos do contorno de um quadrado.

        Args: x_min/x_max/y_min/y_max: limites; divisoes: segmentos por lado.
        Returns: Lista de pontos 2D no contorno, sem cantos duplicados.
        """
        pontos = []

        for i in range(divisoes):
            t = i / divisoes
            pontos.append((x_min + t * (x_max - x_min), y_min))

        for i in range(divisoes):
            t = i / divisoes
            pontos.append((x_max, y_min + t * (y_max - y_min)))

        for i in range(divisoes):
            t = i / divisoes
            pontos.append((x_max - t * (x_max - x_min), y_max))

        for i in range(divisoes):
            t = i / divisoes
            pontos.append((x_min, y_max - t * (y_max - y_min)))

        return pontos


    def gerarCamadas(self,centro_vara, ponto_externo, raio_vara, camadas_deformadas, razao_ballooning):
        """Cria camadas radiais entre a vara e o contorno exterior.

        Args: centro_vara: centro 2D; ponto_externo: destino; raio_vara: raio;
            camadas_deformadas: numero de camadas; razao_ballooning: crescimento.
        Returns: Lista de pontos 2D desde a vara ate ao contorno.
        """
        centro_x, centro_y = centro_vara
        externo_x, externo_y = ponto_externo
        direcao_x = externo_x - centro_x
        direcao_y = externo_y - centro_y
        distancia_externa = np.hypot(direcao_x, direcao_y)

        if distancia_externa <= raio_vara:
            raise ValueError("O contorno externo tem de ficar fora da vara.")

        unidade_x = direcao_x / distancia_externa
        unidade_y = direcao_y / distancia_externa

        espaco_radial = distancia_externa - raio_vara
        pesos = razao_ballooning ** np.arange(camadas_deformadas)  # cria um array com os devidos espaços
        passos = espaco_radial * pesos / np.sum(pesos)

        distancias = [raio_vara]
        distancia_atual = raio_vara
        for passo in passos:
            distancia_atual += passo
            distancias.append(distancia_atual)

        distancias[-1] = distancia_externa#garante que o ultimo ponto seja no ultimo ponto do quadrado

        camadas = []
        for distancia in distancias:
            camadas.append((centro_x + distancia * unidade_x,centro_y + distancia * unidade_y))
        return camadas

    def gerarPontosDoCuboDaVara (self,pontos,
    mapa_pontos,
    x_coords,
    y_coords,
    z_coords,
    intervalo_x_deformado,
    intervalo_y_deformado,
    centro_vara,
    raio_vara,
    divisoes_aresta,
    camadas_deformadas,
    razao_ballooning,
):
        """
        Cria os pontos dos contornos da vara e guarda os seus indices.

        ids_contornos[iz, camada, i]:
            iz -> nivel de altura Z;
            camada -> camada entre a vara e o quadrado;
            i -> posicao ao redor do quadrado.
        """
        x_min = x_coords[intervalo_x_deformado[0]]
        x_max = x_coords[intervalo_x_deformado[1]]
        y_min = y_coords[intervalo_y_deformado[0]]
        y_max = y_coords[intervalo_y_deformado[1]]

        lado_menor = min(x_max - x_min, y_max - y_min)
        if raio_vara >= lado_menor / 2:
            raise ValueError("O raio da vara tem de ser menor que metade do lado do cubo deformado.")

        pontos_quadrado = self.gerarPontosDoQuadrado(x_min, x_max, y_min, y_max,divisoes_aresta)
        centro_x, centro_y = centro_vara
        quantidade_lados = len(pontos_quadrado)
        quantidade_contornos = camadas_deformadas + 1

        ids_contornos = np.empty((len(z_coords), quantidade_contornos, quantidade_lados), dtype=int)

        for iz, z in enumerate(z_coords):
            for i, ponto_externo_2d in enumerate(pontos_quadrado):
                contornos_2d = self.gerarCamadas(
                    (centro_x, centro_y),
                    ponto_externo_2d,
                    raio_vara,
                    camadas_deformadas,
                    razao_ballooning,
                )

                for camada, ponto_2d in enumerate(contornos_2d):
                    ids_contornos[iz, camada, i] = self.adicionarPonto(
                        pontos,
                        mapa_pontos,
                        (ponto_2d[0], ponto_2d[1], z),
                    )

        return ids_contornos
    # =======================================================================
    # ======================Adição de Pontos=================================
    # =======================================================================
    def adicionarCoordenadaObrigatoria(self,coordenadas, valor):
        """Garante que um valor existe num eixo ordenado.

        Args: coordenadas: coordenadas existentes; valor: coordenada obrigatoria.
        Returns: Array ordenado contendo o valor.
        """
        coordenadas = list(coordenadas)#tranforma o array cordenadas em uma lista

        if not any(np.isclose(coordenada, valor) for coordenada in coordenadas):#vai verificar se não existe nenhuma cordenada com esse valor para poder adicionar caso não exista
            coordenadas.append(valor)

        coordenadas = sorted(coordenadas)  # ordena a nova cordenada
        return np.asarray(coordenadas, dtype=float)

    def adicionarPonto(self,pontos, mapa_pontos, coordenadas):
        """Adiciona um ponto apenas quando ainda nao existe.

        Args: pontos: lista mutavel; mapa_pontos: mapa coordenada-indice;
            coordenadas: novo ponto (x, y, z).
        Returns: Indice do ponto novo ou ja existente.
        """
        key = self.chavePonto(coordenadas)

        if key not in mapa_pontos:
            mapa_pontos[key] = len(pontos)
            pontos.append(coordenadas)

        return mapa_pontos[key]
    #========================================CUBOS====================================================
    def gerarCubos(self):
        """Gera os hexaedros da grelha regular base.

        Args: Nao recebe parametros alem da instancia.
        Returns: Array (n, 9), com 8 seguido dos oito indices de cada hexaedro.
        """

        cube_list = np.empty((self.dx * self.dy * self.dz, 9), dtype=int)

        start_points = np.empty((self.dx * self.dy * self.dz, 3), dtype=int)

        i = 0
        for x in range(self.dx):
            for y in range(self.dy):
                for z in range(self.dz):
                    start_points[i][0] = x
                    start_points[i][1] = y
                    start_points[i][2] = z
                    i += 1

        for e in range(self.dx * self.dy * self.dz):
            x = start_points[e][0]
            y = start_points[e][1]
            z = start_points[e][2]
            cube_list[e][0] = 8
            cube_list[e][1] = (z + y * (self.dz + 1) + x * (self.dz + 1) * (self.dy + 1))
            cube_list[e][2] = (z + y * (self.dz + 1) + (x + 1) * (self.dz + 1) * (self.dy + 1))
            cube_list[e][3] = ((z + 1) + y * (self.dz + 1) + (x + 1) * (self.dz + 1) * (self.dy + 1))
            cube_list[e][4] = ((z + 1) + y * (self.dz + 1) + x * (self.dz + 1) * (self.dy + 1))
            cube_list[e][5] = (z + (y + 1) * (self.dz + 1) + x * (self.dz + 1) * (self.dy + 1))
            cube_list[e][6] = (z + (y + 1) * (self.dz + 1) + (x + 1) * (self.dz + 1) * (self.dy + 1))
            cube_list[e][7] = ((z + 1) + (y + 1) * (self.dz + 1) + (x + 1) * (self.dz + 1) * (self.dy + 1))
            cube_list[e][8] = ((z + 1) + (y + 1) * (self.dz + 1) + x * (self.dz + 1) * (self.dy + 1))

        #retorna a lista com os respectivos cubos
        return cube_list

    def gerarCubo(self,ix, iy, iz, quantidade_pontos_y, quantidade_pontos_z):
        """Gera a conectividade de um hexaedro da grelha.

        Args: ix, iy, iz: indice inicial; quantidade_pontos_y/z: dimensoes da grelha.
        Returns: Lista com tipo 8 e os oito indices dos vertices.
        """

        p0 = self.indicePonto(ix, iy, iz, quantidade_pontos_y, quantidade_pontos_z)
        p1 = self.indicePonto(ix + 1, iy, iz, quantidade_pontos_y, quantidade_pontos_z)
        p2 = self.indicePonto(ix + 1, iy + 1, iz, quantidade_pontos_y, quantidade_pontos_z)
        p3 = self.indicePonto(ix, iy + 1, iz, quantidade_pontos_y, quantidade_pontos_z)
        p4 = self.indicePonto(ix, iy, iz + 1, quantidade_pontos_y, quantidade_pontos_z)
        p5 = self.indicePonto(ix + 1, iy, iz + 1, quantidade_pontos_y, quantidade_pontos_z)
        p6 = self.indicePonto(ix + 1, iy + 1, iz + 1, quantidade_pontos_y, quantidade_pontos_z)
        p7 = self.indicePonto(ix, iy + 1, iz + 1, quantidade_pontos_y, quantidade_pontos_z)

        return [8, p0, p1, p2, p3, p4, p5, p6, p7]

    def gerarCubosSemVara(self,intervalos_x,intervalos_y,z_coords,cubo_deformadoA,z_inicio_varaA,z_fim_varaA,quantidade_pontos_y,quantidade_pontos_z,z_inicio_varaB=None,z_fim_varaB=None,cubo_deformadoB=None):
        """
        Gera todos os cubos normais deixando o espaço para a vara.

        No cubo da vara, so salta os intervalos em Z onde a vara existe.
        O resto fica preenchido com cubos normais.
        """
        cubos = []
        quantidade_intervalos_z = len(z_coords) - 1

        for cubo_x, (inicio_x, fim_x) in enumerate(intervalos_x):
            for cubo_y, (inicio_y, fim_y) in enumerate(intervalos_y):
                for ix in range(inicio_x, fim_x):
                    for iy in range(inicio_y, fim_y):
                        for iz in range(quantidade_intervalos_z):
                            z0 = z_coords[iz]
                            z1 = z_coords[iz + 1]

                            if (
                                    (self.ehCuboDeformado(cubo_x, cubo_y, cubo_deformadoA)
                                    and self.intervaloDentroDaVara(z0, z1, z_inicio_varaA, z_fim_varaA))
                            ):
                                continue
                            if (
                                    (self.ehCuboDeformado(cubo_x, cubo_y, cubo_deformadoB)
                                    and self.intervaloDentroDaVara(z0, z1, z_inicio_varaB, z_fim_varaB))
                            ):
                                continue

                            cubos.append(self.gerarCubo(ix, iy, iz, quantidade_pontos_y, quantidade_pontos_z))

        return cubos


    # Este metodo recebe ids_contornos; nao recebe pontos, mapa e coordenadas.
    def gerarCubosDaVara(self,ids_contornos, camadas_deformadas):
        """Liga contornos sucessivos para formar hexaedros deformados.

        Args: ids_contornos: indices por nivel, camada e lado;
            camadas_deformadas: numero de intervalos radiais.
        Returns: Lista de hexaedros deformados.
        """
        cubos_deformados = []
        quantidade_niveis_z = ids_contornos.shape[0]
        quantidade_lados = ids_contornos.shape[2]

        for iz in range(quantidade_niveis_z - 1):
            for camada in range(camadas_deformadas):
                proxima_camada = camada + 1

                for i in range(quantidade_lados):
                    proximo_i = (i + 1) % quantidade_lados

                    cubos_deformados.append([
                        8,
                        ids_contornos[iz, camada, i],
                        ids_contornos[iz, proxima_camada, i],
                        ids_contornos[iz, proxima_camada, proximo_i],
                        ids_contornos[iz, camada, proximo_i],
                        ids_contornos[iz + 1, camada, i],
                        ids_contornos[iz + 1, proxima_camada, i],
                        ids_contornos[iz + 1, proxima_camada, proximo_i],
                        ids_contornos[iz + 1, camada, proximo_i],
                    ])

        return cubos_deformados




    # =======================================TETRAEDROS===============================================
    def divCubesInTetraedros5(self):
        """Divide cada hexaedro final em cinco tetraedros.

        Args: Nao recebe parametros alem da instancia.
        Returns: Array com tipo 4 e quatro indices por tetraedro.
        """
        cube_list = self.final_cube_list
        pontos = self.final_points_list
        c = 0
        tetraedro = np.empty(((len(cube_list) * 5), 5), dtype=int)
        for i in range(len(cube_list)):
            tetraedro[c] = [4, cube_list[i, 1], cube_list[i, 2], cube_list[i, 4], cube_list[i, 5]]
            tetraedro[c + 1] = [4, cube_list[i, 2], cube_list[i, 3], cube_list[i, 4], cube_list[i, 7]]
            tetraedro[c + 2] = [4, cube_list[i, 2], cube_list[i, 4], cube_list[i, 5], cube_list[i, 7]]
            tetraedro[c + 3] = [4, cube_list[i, 2], cube_list[i, 5], cube_list[i, 6], cube_list[i, 7]]
            tetraedro[c + 4] = [4, cube_list[i, 4], cube_list[i, 5], cube_list[i, 7], cube_list[i, 8]]
            c += 5

        for i in range(len(tetraedro)):
            ids = tetraedro[i, 1:5]  # indice dos 4 pontos do tetraedro da posiçao I

            p0 = pontos[ids[0]]
            p1 = pontos[ids[1]]
            p2 = pontos[ids[2]]
            p3 = pontos[ids[3]]

            volume = np.linalg.det(np.array([
                p1 - p0,
                p2 - p0,
                p3 - p0
            ])) / 6

            if volume < 0:
                tetraedro[i, 3], tetraedro[i, 4] = tetraedro[i, 4], tetraedro[i, 3]
        volumes = []

        for i in range(len(tetraedro)):
            ids = tetraedro[i, 1:5]

            p0 = pontos[ids[0]]
            p1 = pontos[ids[1]]
            p2 = pontos[ids[2]]
            p3 = pontos[ids[3]]

            volume = np.linalg.det(np.array([
                p1 - p0,
                p2 - p0,
                p3 - p0
            ])) / 6

            volumes.append(volume)

        return tetraedro

    def divCubesInTetraedros(self):
        """Divide cada hexaedro final em seis tetraedros orientados positivamente.

        Args: Nao recebe parametros alem da instancia.
        Returns: Array com tipo 4 e quatro indices por tetraedro.
        """
        cube_list = self.final_cube_list
        pontos = self.final_points_list
        c = 0
        tetraedro = np.empty(((len(cube_list) * 6), 5), dtype=int)

        for i in range(len(cube_list)):
            tetraedro[c] = [4, cube_list[i, 1], cube_list[i, 2], cube_list[i, 6], cube_list[i, 7]]
            tetraedro[c + 1] = [4, cube_list[i, 1], cube_list[i, 2], cube_list[i, 3], cube_list[i, 7]]
            tetraedro[c + 2] = [4, cube_list[i, 1], cube_list[i, 5], cube_list[i, 6], cube_list[i, 7]]
            tetraedro[c + 3] = [4, cube_list[i, 1], cube_list[i, 5], cube_list[i, 8], cube_list[i, 7]]
            tetraedro[c + 4] = [4, cube_list[i, 1], cube_list[i, 4], cube_list[i, 3], cube_list[i, 7]]
            tetraedro[c + 5] = [4, cube_list[i, 1], cube_list[i, 4], cube_list[i, 8], cube_list[i, 7]]
            c += 6

        for i in range(len(tetraedro)):
            ids = tetraedro[i, 1:5]  # indice dos 4 pontos do tetraedro da posiçao I

            p0 = pontos[ids[0]]
            p1 = pontos[ids[1]]
            p2 = pontos[ids[2]]
            p3 = pontos[ids[3]]

            volume = np.linalg.det(np.array([
                p1 - p0,
                p2 - p0,
                p3 - p0
            ])) / 6

            if volume < 0:
                tetraedro[i, 3], tetraedro[i, 4] = tetraedro[i, 4], tetraedro[i, 3]
        volumes = []

        for i in range(len(tetraedro)):
            ids = tetraedro[i, 1:5]

            p0 = pontos[ids[0]]
            p1 = pontos[ids[1]]
            p2 = pontos[ids[2]]
            p3 = pontos[ids[3]]

            volume = np.linalg.det(np.array([
                p1 - p0,
                p2 - p0,
                p3 - p0
            ])) / 6

            volumes.append(volume)

        return tetraedro

    def divCubesInTetraedrosF(self,cube_list,pontos):
        """Divide cada hexaedro final em seis tetraedros orientados positivamente.

        Args: Nao recebe parametros alem da instancia.
        Returns: Array com tipo 4 e quatro indices por tetraedro.
        """

        c = 0
        tetraedro = np.empty(((len(cube_list) * 6), 5), dtype=int)

        for i in range(len(cube_list)):
            tetraedro[c] = [4, cube_list[i, 1], cube_list[i, 2], cube_list[i, 6], cube_list[i, 7]]
            tetraedro[c + 1] = [4, cube_list[i, 1], cube_list[i, 2], cube_list[i, 3], cube_list[i, 7]]
            tetraedro[c + 2] = [4, cube_list[i, 1], cube_list[i, 5], cube_list[i, 6], cube_list[i, 7]]
            tetraedro[c + 3] = [4, cube_list[i, 1], cube_list[i, 5], cube_list[i, 8], cube_list[i, 7]]
            tetraedro[c + 4] = [4, cube_list[i, 1], cube_list[i, 4], cube_list[i, 3], cube_list[i, 7]]
            tetraedro[c + 5] = [4, cube_list[i, 1], cube_list[i, 4], cube_list[i, 8], cube_list[i, 7]]
            c += 6

        for i in range(len(tetraedro)):
            ids = tetraedro[i, 1:5]  # indice dos 4 pontos do tetraedro da posiçao I

            p0 = pontos[ids[0]]
            p1 = pontos[ids[1]]
            p2 = pontos[ids[2]]
            p3 = pontos[ids[3]]

            volume = np.linalg.det(np.array([
                p1 - p0,
                p2 - p0,
                p3 - p0
            ])) / 6

            if volume < 0:
                tetraedro[i, 3], tetraedro[i, 4] = tetraedro[i, 4], tetraedro[i, 3]
        volumes = []

        for i in range(len(tetraedro)):
            ids = tetraedro[i, 1:5]

            p0 = pontos[ids[0]]
            p1 = pontos[ids[1]]
            p2 = pontos[ids[2]]
            p3 = pontos[ids[3]]

            volume = np.linalg.det(np.array([
                p1 - p0,
                p2 - p0,
                p3 - p0
            ])) / 6

            volumes.append(volume)

        return tetraedro

    # ========================================BUILDER=================================================
    def gerarMalhaPlacasParalelas(self):
        """Reserva a geracao da malha de placas paralelas.

        Args: Nao recebe parametros alem da instancia.
        Returns: None; funcionalidade ainda nao implementada.
        """
        pass
    def gerarMalha2Vara(
            self,
            cubo_varaA_X, cubo_varaA_Y, rA, cA, max_divA, min_divA, camadasA, ballooningA,
            cubo_varaB_X, cubo_varaB_Y, rB, cB, max_divB, min_divB, camadasB, ballooningB,
    ):
        """Gera uma malha com duas varas de configuracoes diferentes."""
        origem = (0.0, 0.0, 0.0)
        tamanho_cubo_x = self.sx / self.dx
        tamanho_cubo_y = self.sy / self.dy
        tamanho_cubo_z = self.sz / self.dz

        z_fim_A = self.sz
        z_inicio_A = z_fim_A - cA
        z_fim_B = self.sz
        z_inicio_B = z_fim_B - cB

        centro_vara_a = self.calcularCentroDoCubo(
            origem, cubo_varaA_X, cubo_varaA_Y, tamanho_cubo_x, tamanho_cubo_y,
        )
        centro_vara_b = self.calcularCentroDoCubo(
            origem, cubo_varaB_X, cubo_varaB_Y, tamanho_cubo_x, tamanho_cubo_y,
        )
        self.varas_ativas = [
            {"centro": centro_vara_a, "raio": rA, "z_inicio": z_inicio_A, "z_fim": z_fim_A},
            {"centro": centro_vara_b, "raio": rB, "z_inicio": z_inicio_B, "z_fim": z_fim_B},
        ]

        self.balloning = ballooningA
        div_x_A = self.calcularDivisoesPorEixo(self.dx, cubo_varaA_X, max_divA, min_divA)
        div_y_A = self.calcularDivisoesPorEixo(self.dy, cubo_varaA_Y, max_divA, min_divA)
        self.balloning = ballooningB
        div_x_B = self.calcularDivisoesPorEixo(self.dx, cubo_varaB_X, max_divB, min_divB)
        div_y_B = self.calcularDivisoesPorEixo(self.dy, cubo_varaB_Y, max_divB, min_divB)
        divisoes_x = np.maximum(div_x_A, div_x_B)
        divisoes_y = np.maximum(div_y_A, div_y_B)

        div_z_A = self.calcularDivisoesZComVara(
            self.dz, tamanho_cubo_z, z_inicio_A, z_fim_A,
            max_divA, min_divA, ballooningA,
        )
        div_z_B = self.calcularDivisoesZComVara(
            self.dz, tamanho_cubo_z, z_inicio_B, z_fim_B,
            max_divB, min_divB, ballooningB,
        )
        divisoes_z = np.maximum(div_z_A, div_z_B)

        x_coords, intervalos_x = self.gerarCoordenadasPorEixo(self.dx, tamanho_cubo_x, divisoes_x)
        y_coords, intervalos_y = self.gerarCoordenadasPorEixo(self.dy, tamanho_cubo_y, divisoes_y)
        z_coords, intervalos_z = self.gerarCoordenadasPorEixo(self.dz, tamanho_cubo_z, divisoes_z)
        z_coords = self.adicionarCoordenadaObrigatoria(z_coords, z_inicio_A)
        z_coords = self.adicionarCoordenadaObrigatoria(z_coords, z_inicio_B)
        z_coords = self.adicionarCoordenadaObrigatoria(z_coords, self.sz)

        z_coords_A = z_coords[(z_coords >= z_inicio_A - 1e-12) & (z_coords <= z_fim_A + 1e-12)]
        z_coords_B = z_coords[(z_coords >= z_inicio_B - 1e-12) & (z_coords <= z_fim_B + 1e-12)]

        pontos_base = self.gerarPointsOrdenados(x_coords, y_coords, z_coords)
        mapa_pontos = self.gerarMapaPontos(pontos_base)
        pontos = [tuple(ponto) for ponto in pontos_base]

        cubos_normais = self.gerarCubosSemVara(
            intervalos_x, intervalos_y, z_coords,
            (cubo_varaA_X, cubo_varaA_Y), z_inicio_A, z_fim_A,
            len(y_coords), len(z_coords),
            z_inicio_B, z_fim_B, (cubo_varaB_X, cubo_varaB_Y),
        )

        cubos_deformadosA = self.gerarCubosDaVara(self.gerarPontosDoCuboDaVara(
            pontos, mapa_pontos, x_coords, y_coords, z_coords_A,
            intervalos_x[cubo_varaA_X],
            intervalos_y[cubo_varaA_Y],
            centro_vara_a, rA, max_divA, camadasA, ballooningA,
        ), camadasA)
        cubos_deformadosB = self.gerarCubosDaVara(self.gerarPontosDoCuboDaVara(
            pontos, mapa_pontos, x_coords, y_coords, z_coords_B,
            intervalos_x[cubo_varaB_X],
            intervalos_y[cubo_varaB_Y],
            centro_vara_b, rB, max_divB, camadasB, ballooningB,
        ), camadasB)

        pontos_totais = np.asarray(pontos, dtype=float)
        cubos_totais = np.asarray(
            cubos_normais + cubos_deformadosA + cubos_deformadosB,
            dtype=int,
        )
        self.final_points_list = pontos_totais
        self.final_cube_list = cubos_totais
        self.final_tetraedro_list = self.divCubesInTetraedrosF(cubos_totais, pontos_totais)
        return pontos_totais, cubos_totais, cubos_normais, cubos_deformadosA, cubos_deformadosB
    def gerarMalha1Vara(self,cubo_vara_X,cubo_vara_Y,r,c,max_div,min_div,camadas_deformadas,balloning):
        """Gera uma malha refinada em torno de uma vara.

        Args: cubo_vara_X/Y: cubo da vara; r: raio; c: comprimento;
            max_div/min_div: limites de refinamento; camadas_deformadas:
            camadas radiais; balloning: razao de crescimento.
        Returns: pontos, todos os cubos, cubos normais e cubos deformados.
        """
        self.balloning = balloning
        cubo_deformado=(cubo_vara_X,cubo_vara_Y)
        origem = (0.0, 0.0, 0.0)
        tamanho_cubo_x = self.sx / self.dx
        tamanho_cubo_y = self.sy / self.dy
        tamanho_cubo_z = self.sz / self.dz
        z_fim_vara = self.sz
        z_inicio_vara = z_fim_vara - c

        centro_vara=self.calcularCentroDoCubo(origem,cubo_vara_X,cubo_vara_Y,tamanho_cubo_x,tamanho_cubo_y)
        self.varas_ativas = [
            {"centro": centro_vara, "raio": r, "z_inicio": z_inicio_vara, "z_fim": z_fim_vara}
        ]

        #Divisões dos cubos assim obtendo as suas respectivas divizoes
        divisoes_x_por_cubo = self.calcularDivisoesPorEixo(
            self.dx,
            cubo_vara_X,
            max_div,
            min_div,
        )
        divisoes_y_por_cubo = self.calcularDivisoesPorEixo(
            self.dy,
            cubo_vara_Y,
            max_div,
            min_div,
        )
        divisoes_z_por_cubo_lista = self.calcularDivisoesZComVara(
            self.dz,
            tamanho_cubo_z,
            z_inicio_vara,
            z_fim_vara,
            max_div,
            min_div,self.balloning
        )
        x_coords, intervalos_x = self.gerarCoordenadasPorEixo(self.dx, tamanho_cubo_x, divisoes_x_por_cubo, origem[0])
        y_coords, intervalos_y = self.gerarCoordenadasPorEixo(self.dy, tamanho_cubo_y, divisoes_y_por_cubo, origem[1])
        z_coords, intervalos_z = self.gerarCoordenadasPorEixo(self.dz, tamanho_cubo_z, divisoes_z_por_cubo_lista,
                                                         origem[2])
        z_coords = self.adicionarCoordenadaObrigatoria(z_coords, z_inicio_vara)
        z_coords = self.adicionarCoordenadaObrigatoria(z_coords, z_fim_vara)
        z_coords_vara = z_coords[
            (z_coords >= z_inicio_vara - 1e-12)
            & (z_coords <= z_fim_vara + 1e-12)
            ]
        #lista de pontos inicial
        pontos_base=self.gerarPointsOrdenados(x_coords,y_coords,z_coords)
        mapa_pontos = self.gerarMapaPontos(pontos_base)
        pontos = [tuple(ponto) for ponto in pontos_base]
        quantidade_pontos_y = len(y_coords)
        quantidade_pontos_z = len(z_coords)

        cubos_normais = self.gerarCubosSemVara(
            intervalos_x,
            intervalos_y,
            z_coords,
            cubo_deformado,
            z_inicio_vara,
            z_fim_vara,
            quantidade_pontos_y,
            quantidade_pontos_z,
        )
        cubos_deformados = self.gerarCubosDaVara(self.gerarPontosDoCuboDaVara(
            pontos,
            mapa_pontos,
            x_coords,
            y_coords,
            z_coords_vara,
            intervalos_x[cubo_vara_X],
            intervalos_y[cubo_vara_Y],
            centro_vara,
            r,
            max_div,
            camadas_deformadas,
            balloning ),camadas_deformadas
        )
        pontos_totais = np.asarray(pontos, dtype=float)
        cubos_totais = np.asarray(cubos_normais + cubos_deformados, dtype=int)
        self.final_points_list = pontos_totais
        self.final_cube_list = cubos_totais
        self.final_tetraedro_list = self.divCubesInTetraedrosF(cubos_totais, pontos_totais)
        return pontos_totais, cubos_totais,cubos_normais,cubos_deformados

    def gerarMalhaNormal(self):
        pontos = self.gerarPointsOrdenados()
        cubos = self.gerarCubos()

        cubos, pontos = self.reorganizar(cubos,pontos)

        self.varas_ativas = []
        self.final_points_list = pontos
        self.final_cube_list = cubos
        self.final_vector = self.gerarVetor(pontos)
        self.final_tetraedro_list=self.divCubesInTetraedrosF(cubos, pontos)
        return pontos, cubos
    # =======================================Auxiliares===============================================

    def calcularCentroDoCubo(self,origem, cubo_x, cubo_y, tamanho_cubo_x, tamanho_cubo_y):
        """
        :param cubo_x:eixo x onde está o cubo que contem a vara
        :param cubo_y: eixo y onde está o cubo que contem a vara
        :param tamanho_cubo_x: dimensões do cubo
        :param tamanho_cubo_y: dimensões do cubo
        :return: onde estara a vara no eixo x e y
        """
        centro_x = origem[0] + (cubo_x + 0.5) * tamanho_cubo_x
        centro_y = origem[1] + (cubo_y + 0.5) * tamanho_cubo_y

        return centro_x, centro_y

    def calcularDivisoesPorEixo(self,numero_cubos,cubo_vara_a,divisoes_perto,divisoes_longe,cubo_vara_b=None):
        """
        Calcula as divisoes de um eixo usando uma ou duas varas.
        :param numero_cubos: numero de cubos/espaço no eixo
        :param cubo_vara_a: cubo que tem uma vara
        :param divisoes_perto: valor maximo de divisões
        :param divisoes_longe: valor minimo de divisões
        :param razao_ballooning: razao de crescimento
        :param cubo_vara_b: cubo que tem outra vara
        :return: um array com os respectivos divizões neste eixo
        """
        divisoes = []

        if cubo_vara_b is None or cubo_vara_a == cubo_vara_b:
            for cubo in range(numero_cubos):
                distancia = abs(cubo - cubo_vara_a)
                divisoes_do_cubo = round(divisoes_perto / (self.balloning ** distancia))
                divisoes_do_cubo = max(divisoes_longe, divisoes_do_cubo)
                divisoes.append(divisoes_do_cubo)

            return np.asarray(divisoes, dtype=int)
        else:
            vara_a = min(cubo_vara_a, cubo_vara_b)
            vara_b = max(cubo_vara_a, cubo_vara_b)
            meio = (vara_a + vara_b) / 2
            for cubo in range(numero_cubos):
                distancia_ate_vara_mais_proxima = min(abs(cubo - vara_a), abs(cubo - vara_b))

                divisoes_do_cubo = round(divisoes_perto / (self.balloning ** distancia_ate_vara_mais_proxima))
                divisoes_do_cubo = max(divisoes_longe, divisoes_do_cubo)
                divisoes.append(divisoes_do_cubo)

            return np.asarray(divisoes, dtype=int)

    def distanciaAteIntervalo(self,valor, inicio, fim, tamanho_cubo):
        """Calcula a distancia discreta de um valor a um intervalo.

        Args: valor: coordenada; inicio/fim: limites; tamanho_cubo: escala do passo.
        Returns: Distancia inteira em numero de cubos.
        """
        if inicio <= valor <= fim:
            return 0

        if valor < inicio:
            return int((inicio - valor) / tamanho_cubo) + 1

        return int((valor - fim) / tamanho_cubo) + 1

    def calcularDivisoesZComVara(self,numero_cubos_z, tamanho_cubo_z, z_inicio_vara, z_fim_vara, divisoes_perto,divisoes_longe,razao_ballooning):
        """Calcula o refinamento de cada cubo no eixo Z.

        Args: numero_cubos_z/tamanho_cubo_z: geometria do eixo; z_inicio_vara/
            z_fim_vara: extensao da vara; divisoes_perto/longe: limites;
            razao_ballooning: taxa de reducao do refinamento.
        Returns: Array de divisoes por cubo em Z.
        """
        divisoes = []
        for cubo_z in range(numero_cubos_z):
            centro_z = (cubo_z + 0.5) * tamanho_cubo_z
            distancia = self.distanciaAteIntervalo(
                centro_z,
                z_inicio_vara,
                z_fim_vara,
                tamanho_cubo_z
            )

            divisoes_do_cubo = round(divisoes_perto / (razao_ballooning ** distancia))
            divisoes_do_cubo = max(divisoes_longe, divisoes_do_cubo)
            divisoes.append(divisoes_do_cubo)
        return np.asarray(divisoes, dtype=int)

#=======================================Verificadores==========================================================================
    def intervaloDentroDaVara(self,z0, z1, z_inicio_vara, z_fim_vara):
        """Verifica se um intervalo Z esta dentro de uma vara.

        Args: z0/z1: intervalo; z_inicio_vara/z_fim_vara: limites da vara.
        Returns: Booleano.
        """
        if z_inicio_vara == None or z_fim_vara == None:
            return False
        return z0 >= z_inicio_vara and z1 <= z_fim_vara

    def ehCuboDeformado(self,cubo_x, cubo_y, cubo_deformado):
        """Verifica se um cubo corresponde ao cubo deformado.

        Args: cubo_x/cubo_y: indices; cubo_deformado: par esperado ou None.
        Returns: Booleano.
        """
        if cubo_deformado == None:
            return False
        return (cubo_x, cubo_y) == cubo_deformado



    def isFronteiraSuperior(self,i):
        """Indica se o ponto i pertence ao topo. Args: i: indice. Returns: bool."""
        if  self.points_list[i][2] == self.sz:
            return True
        return False
    def isFronteiraInferior(self,i):
        """Indica se o ponto i pertence a base. Args: i: indice. Returns: bool."""
        if  self.points_list[i][2] == 0:
            return True
        return False

    def isFronteiratLateral(self,i):
        """Indica se o ponto i pertence a uma lateral. Args: i: indice. Returns: bool."""
        if ( self.points_list[i][2] != self.sz and  self.points_list[i][2] != 0) and (
                ( self.points_list[i][1] == self.sy or  self.points_list[i][1] == 0) or (
                 self.points_list[i][0] == self.sx or  self.points_list[i][0] == 0)):
            return True
        return False

    def isPontoLivre(self,i):
        """Indica se o ponto i nao pertence a fronteira. Args: i: indice. Returns: bool."""
        if not self.isFronteiratLateral(i) and not self.isFronteiraInferior(i) and not self.isFronteiraSuperior(i):
            return True
        return False
    def isFronteiraNaVara(self,i,pontos):
        """Retorna True se o ponto pertence à superfície de uma vara."""
        x, y, z = pontos[i]

        for vara in self.varas_ativas:
            centro_x, centro_y = vara["centro"]
            distancia = np.hypot(x - centro_x, y - centro_y)

            esta_na_altura_da_vara = vara["z_inicio"] <= z <= vara["z_fim"]
            esta_no_raio_da_vara = np.isclose(distancia, vara["raio"])

            if esta_na_altura_da_vara and esta_no_raio_da_vara:
                return True

        return False

    def isLongeDaVara(self, i,pontos, distancia_minima=7.6):
        """Retorna True se o ponto estiver longe de todas as varas."""
        x, y, z = pontos[i]

        for vara in self.varas_ativas:
            centro_x, centro_y = vara["centro"]

            distancia_xy = np.hypot(x - centro_x, y - centro_y) - vara["raio"]

            if z < vara["z_inicio"]:
                distancia_z = vara["z_inicio"] - z
            elif z > vara["z_fim"]:
                distancia_z = z - vara["z_fim"]
            else:
                distancia_z = 0

            distancia = np.hypot(max(0, distancia_xy), distancia_z)

            if distancia < distancia_minima:
                return False

        return True

    ###################################################################################



    def gerarVetor(self,pontos):
        """Conta os grupos de pontos da malha base.

        Args: Nao recebe parametros alem da instancia.
        Returns: Array [livres+lateral, superiores, inferiores].
        """
        front_s = 0 #fronteira superior
        front_i = 0 #fronteira Inferior
        front_lat = 0 #fronteira Lateral
        front_livre = 0  #Pontos Livres

        for i in range(len(pontos)):

            if  self.isFronteiraSuperior(i):
                front_s += 1
            elif self.isFronteiraInferior(i):
                front_i += 1
            elif self.isFronteiratLateral(i):
                front_lat += 1
            else:
                front_livre +=1

        return np.array([front_livre + front_lat, front_s, front_i])
    def gerarVetordaVara(self,pontos):
        """Conta os grupos de pontos da malha base.

        Args: Nao recebe parametros alem da instancia.
        Returns: Array [livres+lateral, superiores, inferiores].
        """
        front_V = 0 #fronteira na vara
        front_L = 0 #fronteira longe da vara
        front_livre = 0  #Pontos Livres

        for i in range(len(pontos)):

            if  self.isFronteiraNaVara(i,pontos):
                front_V += 1
            elif self.isLongeDaVara(i,pontos):
                front_L += 1
            else:
                front_livre +=1

        return np.array([front_livre , front_V, front_L])



    def reorganizarVara(self,cubos,pontos):
        """Reordena pontos por tipo de fronteira e atualiza a conectividade.

        Args: Nao recebe parametros alem da instancia.
        Returns: Tupla (cubos reindexados, pontos reordenados).
        """


        newpoints = np.empty(pontos.shape, dtype=float)

        mapa = np.full(len(pontos), -1, dtype=int)
        novoid = 0

        for i in range(len(pontos)):
            if not self.isFronteiraNaVara(i,pontos) and not self.isLongeDaVara(i,pontos):
                    newpoints[novoid] = pontos[i]
                    mapa[i] = novoid
                    novoid += 1

        for i in range(len(pontos)):
            if self.isFronteiraNaVara(i,pontos):
                    newpoints[novoid] = pontos[i]
                    mapa[i] = novoid
                    novoid += 1
        for i in range(len(pontos)):
            if self.isLongeDaVara(i,pontos):
                    newpoints[novoid] = pontos[i]
                    mapa[i] = novoid
                    novoid += 1
        newcube = np.empty(cubos.shape, dtype=int)
        for i in range(len(cubos)):
            newcube[i][0] = 8
            newcube[i][1] = mapa[cubos[i][1]]
            newcube[i][2] = mapa[cubos[i][2]]
            newcube[i][3] = mapa[cubos[i][3]]
            newcube[i][4] = mapa[cubos[i][4]]
            newcube[i][5] = mapa[cubos[i][5]]
            newcube[i][6] = mapa[cubos[i][6]]
            newcube[i][7] = mapa[cubos[i][7]]
            newcube[i][8] = mapa[cubos[i][8]]

        if np.any(mapa == -1):
            print("ERRO: existem pontos não classificados")

        return newcube, newpoints

    def reorganizar(self,cubos,pontos):
        """Reordena pontos por tipo de fronteira e atualiza a conectividade.

        Args: Nao recebe parametros alem da instancia.
        Returns: Tupla (cubos reindexados, pontos reordenados).
        """


        self.points_list=pontos

        newpoints = np.empty(pontos.shape, dtype=float)

        mapa = np.full(len(pontos), -1, dtype=int)
        novoid = 0

        for i in range(len(pontos)):
            if self.isPontoLivre(i):
                    newpoints[novoid] = pontos[i]
                    mapa[i] = novoid
                    novoid += 1
        for i in range(len(pontos)):
            if self.isFronteiratLateral(i):
                    newpoints[novoid] = pontos[i]
                    mapa[i] = novoid
                    novoid += 1
        for i in range(len(pontos)):
            if self.isFronteiraSuperior(i):
                    newpoints[novoid] = pontos[i]
                    mapa[i] = novoid
                    novoid += 1
        for i in range(len(pontos)):
            if self.isFronteiraInferior(i):
                    newpoints[novoid] = pontos[i]
                    mapa[i] = novoid
                    novoid += 1
        newcube = np.empty(cubos.shape, dtype=int)
        for i in range(len(cubos)):
            newcube[i][0] = 8
            newcube[i][1] = mapa[cubos[i][1]]
            newcube[i][2] = mapa[cubos[i][2]]
            newcube[i][3] = mapa[cubos[i][3]]
            newcube[i][4] = mapa[cubos[i][4]]
            newcube[i][5] = mapa[cubos[i][5]]
            newcube[i][6] = mapa[cubos[i][6]]
            newcube[i][7] = mapa[cubos[i][7]]
            newcube[i][8] = mapa[cubos[i][8]]

        if np.any(mapa == -1):
            print("ERRO: existem pontos não classificados")

        return newcube, newpoints

    def removerPontosNaoUtilizados(self, cubos, pontos):
        """
        Remove pontos que não pertencem a nenhum cubo
        e atualiza os índices dos cubos.
        """

        # 1. Descobrir quais pontos são utilizados/cria um array com a mesma dimensão que o array de pontos orrginal tudo a false
        ponto_usado = np.full(len(pontos), False, dtype=bool)

        for cubo in cubos:#vai percorer todos os cubos e todos os indices e vai verificar se esse indice foi referenciado se sim muda de false para true
            for posicao in range(1, 9):
                indice_ponto = cubo[posicao]
                ponto_usado[indice_ponto] = True

        # 2. Criar o mapa e a nova lista de pontos
        mapa = np.full(len(pontos), -1, dtype=int)
        novos_pontos = []

        novo_indice = 0

        for i in range(len(pontos)):#vai percorrer todos os pontos da lista de pontos
            if ponto_usado[i]:#se esse ponto estiver marcado como verdadeiro ele vai ser colocado na lista de pontos
                novos_pontos.append(pontos[i])

                mapa[i] = novo_indice#o mapa vai na possição do ponto antigo receber qual sera o novo ponto assim podendo comparar
                novo_indice += 1

        # 3. Copiar os cubos, substituindo os índices antigos
        novos_cubos = []

        for cubo in cubos:
            novo_cubo = [8]

            for posicao in range(1, 9):
                indice_antigo = cubo[posicao]
                indice_novo = mapa[indice_antigo]

                novo_cubo.append(indice_novo)

            novos_cubos.append(novo_cubo)

        return (
            np.asarray(novos_cubos, dtype=int),
            np.asarray(novos_pontos, dtype=float),
        )

    def clean(self, cubos, pontos):
        cubos, pontos = self.removerPontosNaoUtilizados(cubos,pontos)

        if self.varas_ativas:
            cubos, pontos = self.reorganizarVara(cubos, pontos)
        else:
            cubos, pontos = self.reorganizar(cubos,pontos)

        tetraedros = self.divCubesInTetraedrosF(cubos, pontos)

        return tetraedros, pontos

#Getters e Setters

    def getCubesList(self):
        """Devolve os cubos finais. Args: nenhum. Returns: array de cubos."""
        return self.final_cube_list
    def getPointsList(self):
        """Devolve os pontos finais. Args: nenhum. Returns: array de pontos."""
        return self.final_points_list
    def getTetraedrosList(self):
        """Devolve a malha tetraedrica. Args: nenhum. Returns: array de tetraedros."""
        return self.final_tetraedro_list
    def getVetorList(self):
        """Devolve as contagens de fronteira. Args: nenhum. Returns: vetor de contagens."""
        return self.final_vector

