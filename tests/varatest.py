import argparse

import numpy as np


from  mesh.Builder import Malha

RAIO_VARA = 0.00794
COMPRIMENTO_VARA = 3.3
DIVISOES_CUBO_DEFORMADO = 8
DIVISOES_CUBO_LONGE = 1
CAMADAS_DEFORMADAS = 8
RAZAO_BALLOONING = 1.55
CASAS_ARREDONDAMENTO = 12


def chavePonto(coordenadas):
    return tuple(np.round(coordenadas, CASAS_ARREDONDAMENTO))


def indicePonto(ix, iy, iz, quantidade_pontos_y, quantidade_pontos_z):
    """
    Transforma a posicao de um ponto na grelha 3D em indice de lista.

    A ordem e a mesma ideia do Builder:
        primeiro anda em Z,
        depois em Y,
        depois em X.
    """
    return iz + iy * quantidade_pontos_z + ix * quantidade_pontos_z * quantidade_pontos_y


def gerarCoordenadasPorCubo(numero_cubos, tamanho_cubo, divisoes_por_cubo, origem=0.0):
    """
    Cria as coordenadas de um eixo.

    Cada cubo base pode ter uma quantidade diferente de divisoes. Exemplo:

        numero_cubos = 3
        tamanho_cubo = 1
        divisoes_por_cubo = [1, 4, 1]

    Resultado:
        o cubo do meio fica mais dividido que os cubos das pontas.
    """
    coordenadas = [origem]
    intervalos = []

    for cubo in range(numero_cubos):
        inicio = origem + cubo * tamanho_cubo
        divisoes = int(divisoes_por_cubo[cubo])
        indice_inicio = len(coordenadas) - 1

        for divisao in range(1, divisoes + 1):
            coordenadas.append(inicio + divisao * tamanho_cubo / divisoes)

        indice_fim = len(coordenadas) - 1
        intervalos.append((indice_inicio, indice_fim))

    return np.asarray(coordenadas, dtype=float), intervalos



def adicionarCoordenadaObrigatoria(coordenadas, valor):
    """
    Garante que uma coordenada importante existe na grelha.

    Para a vara, isto evita que a ponta inferior fique no meio de um elemento.
    """
    coordenadas = list(coordenadas)

    if not any(np.isclose(coordenada, valor) for coordenada in coordenadas):
        coordenadas.append(valor)

    coordenadas = sorted(coordenadas)#ordena a nova cordenada
    return np.asarray(coordenadas, dtype=float)


def gerarPontosOrdenados(x_coords, y_coords, z_coords):
    pontos = np.empty((len(x_coords) * len(y_coords) * len(z_coords), 3), dtype=float)

    i = 0
    for x in x_coords:
        for y in y_coords:
            for z in z_coords:
                pontos[i] = (x, y, z)
                i += 1

    return pontos


def gerarMapaPontos(pontos):
    mapa = {}
    for i, ponto in enumerate(pontos):
        mapa[chavePonto(ponto)] = i
    return mapa


def adicionarPonto(pontos, mapa_pontos, coordenadas):
    key = chavePonto(coordenadas)

    if key not in mapa_pontos:
        mapa_pontos[key] = len(pontos)
        pontos.append(coordenadas)

    return mapa_pontos[key]


def limitarIndiceCubo(cubo, numero_cubos, nome):

    if cubo < 0 or cubo >= numero_cubos:
        raise ValueError(f"{nome} tem de estar entre 0 e {numero_cubos - 1}.")

    return cubo


def calcularCentroDoCubo(origem, cubo_x, cubo_y, tamanho_cubo_x, tamanho_cubo_y):
    centro_x = origem[0] + (cubo_x + 0.5) * tamanho_cubo_x
    centro_y = origem[1] + (cubo_y + 0.5) * tamanho_cubo_y

    return centro_x, centro_y


def calcularDivisoesPorEixo(
    numero_cubos,
    cubo_vara_a,
    divisoes_perto,
    divisoes_longe,
    cubo_vara_b=None,
    razao_ballooning=RAZAO_BALLOONING,
):
    """
    Calcula as divisoes de um eixo usando uma ou duas varas.

    Uma vara:
        a divisao cai conforme a distancia ate essa vara.

    Duas varas:
        perto de uma vara fica no maximo;
        no meio entre as varas fica no valor medio;
        fora das varas cai conforme a distancia ate a vara mais proxima.
    """
    divisoes = []

    if cubo_vara_b is None or cubo_vara_a == cubo_vara_b:
        for cubo in range(numero_cubos):
            distancia = abs(cubo - cubo_vara_a)
            divisoes_do_cubo = round(divisoes_perto / (razao_ballooning ** distancia))
            divisoes_do_cubo = max(divisoes_longe, divisoes_do_cubo)
            divisoes.append(divisoes_do_cubo)

        return np.asarray(divisoes, dtype=int)
    else:
        vara_a = min(cubo_vara_a, cubo_vara_b)
        vara_b = max(cubo_vara_a, cubo_vara_b)
        meio = (vara_a + vara_b) / 2
        for cubo in range(numero_cubos):
            distancia_ate_vara_mais_proxima = min(abs(cubo - vara_a), abs(cubo - vara_b))
            divisoes_do_cubo = round(divisoes_perto / (razao_ballooning ** distancia_ate_vara_mais_proxima))
            divisoes_do_cubo = max(divisoes_longe, divisoes_do_cubo)
            divisoes.append(divisoes_do_cubo)

        return np.asarray(divisoes, dtype=int)

"""
def calcularDivisoesZComVara(numero_cubos_z, tamanho_cubo_z, z_inicio_vara, z_fim_vara, divisoes_perto, divisoes_longe):
    
    #Calcula as divisoes em Z com mais detalhe perto do comprimento da vara.
  
    divisoes = []

    for cubo_z in range(numero_cubos_z):
        z0 = cubo_z * tamanho_cubo_z
        z1 = (cubo_z + 1) * tamanho_cubo_z
        centro_z = (z0 + z1) / 2

        if z_inicio_vara <= centro_z <= z_fim_vara:
            distancia = 0
        elif centro_z < z_inicio_vara:
            distancia = int(np.floor((z_inicio_vara - centro_z) / tamanho_cubo_z)) + 1
        else:
            distancia = int(np.floor((centro_z - z_fim_vara) / tamanho_cubo_z)) + 1

        divisoes_do_cubo = max(divisoes_longe, divisoes_perto - distancia)
        divisoes.append(divisoes_do_cubo)

    return np.asarray(divisoes, dtype=int)
"""


def distanciaAteIntervalo( valor, inicio, fim, tamanho_cubo):
    if inicio <= valor <= fim:
        return 0

    if valor < inicio:
        return int((inicio - valor) / tamanho_cubo) + 1

    return int((valor - fim) / tamanho_cubo) + 1


def calcularDivisoesZComVara( numero_cubos_z, tamanho_cubo_z, z_inicio_vara, z_fim_vara, divisoes_perto,
                             divisoes_longe, razao_ballooning=RAZAO_BALLOONING):
    divisoes = []
    for cubo_z in range(numero_cubos_z):
        centro_z = (cubo_z + 0.5) * tamanho_cubo_z
        distancia = distanciaAteIntervalo(
            centro_z,
            z_inicio_vara,
            z_fim_vara,
            tamanho_cubo_z
        )

        divisoes_do_cubo = round(divisoes_perto / (razao_ballooning ** distancia))
        divisoes_do_cubo = max(divisoes_longe, divisoes_do_cubo)
        divisoes.append(divisoes_do_cubo)
    return np.asarray(divisoes, dtype=int)

def intervaloDentroDaVara(z0, z1, z_inicio_vara, z_fim_vara):
    return z0 >= z_inicio_vara and z1 <= z_fim_vara
def ehCuboDeformado(cubo_x, cubo_y, cubo_deformado):
    return (cubo_x, cubo_y) == cubo_deformado

def gerarCubo(ix, iy, iz, quantidade_pontos_y, quantidade_pontos_z):
    p0 = indicePonto(ix, iy, iz, quantidade_pontos_y, quantidade_pontos_z)
    p1 = indicePonto(ix + 1, iy, iz, quantidade_pontos_y, quantidade_pontos_z)
    p2 = indicePonto(ix + 1, iy + 1, iz, quantidade_pontos_y, quantidade_pontos_z)
    p3 = indicePonto(ix, iy + 1, iz, quantidade_pontos_y, quantidade_pontos_z)
    p4 = indicePonto(ix, iy, iz + 1, quantidade_pontos_y, quantidade_pontos_z)
    p5 = indicePonto(ix + 1, iy, iz + 1, quantidade_pontos_y, quantidade_pontos_z)
    p6 = indicePonto(ix + 1, iy + 1, iz + 1, quantidade_pontos_y, quantidade_pontos_z)
    p7 = indicePonto(ix, iy + 1, iz + 1, quantidade_pontos_y, quantidade_pontos_z)

    return [8, p0, p1, p2, p3, p4, p5, p6, p7]


def gerarCubosNormais(
    intervalos_x,
    intervalos_y,
    z_coords,
    cubo_deformado,
    z_inicio_vara,
    z_fim_vara,
    quantidade_pontos_y,
    quantidade_pontos_z,
):
    """
    Gera todos os cubos normais.

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
                            ehCuboDeformado(cubo_x, cubo_y, cubo_deformado)
                            and intervaloDentroDaVara(z0, z1, z_inicio_vara, z_fim_vara)
                        ):
                            continue

                        cubos.append(gerarCubo(ix, iy, iz, quantidade_pontos_y, quantidade_pontos_z))

    return cubos


def gerarPontosDoQuadrado(x_min, x_max, y_min, y_max, divisoes_aresta):
    """
    Gera pontos no contorno quadrado do cubo deformado.

    Se divisoes_aresta = 4, cada lado do quadrado tem 4 pedacos.
    O total de pontos no contorno e 4 * divisoes_aresta.
    """
    pontos = []

    for i in range(divisoes_aresta):
        t = i / divisoes_aresta
        pontos.append((x_min + t * (x_max - x_min), y_min))

    for i in range(divisoes_aresta):
        t = i / divisoes_aresta
        pontos.append((x_max, y_min + t * (y_max - y_min)))

    for i in range(divisoes_aresta):
        t = i / divisoes_aresta
        pontos.append((x_max - t * (x_max - x_min), y_max))

    for i in range(divisoes_aresta):
        t = i / divisoes_aresta
        pontos.append((x_min, y_max - t * (y_max - y_min)))

    return pontos


def gerarContornosEntreVaraEQuadrado(centro_vara, ponto_externo, raio_vara, camadas_deformadas, razao_ballooning):
    """
    Cria varios pontos entre a vara e o contorno do cubo deformado.

    As primeiras camadas ficam pequenas perto da vara. Depois as distancias
    crescem progressivamente ate chegar ao quadrado exterior.
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
    pesos = razao_ballooning ** np.arange(camadas_deformadas)#cria um array com os devidos espaços
    passos = espaco_radial * pesos / np.sum(pesos)

    distancias = [raio_vara]
    distancia_atual = raio_vara
    for passo in passos:
        distancia_atual += passo
        distancias.append(distancia_atual)

    distancias[-1] = distancia_externa

    camadas = []
    for distancia in distancias:
        camadas.append((centro_x + distancia * unidade_x, centro_y + distancia * unidade_y))
    return camadas


def gerarIdsDosContornosDaVara(
    pontos,
    mapa_pontos,
    z_coords,
    pontos_quadrado,
    centro_vara,
    raio_vara,
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
    centro_x, centro_y = centro_vara
    quantidade_lados = len(pontos_quadrado)
    quantidade_contornos = camadas_deformadas + 1

    ids_contornos = np.empty((len(z_coords), quantidade_contornos, quantidade_lados), dtype=int)

    for iz, z in enumerate(z_coords):
        for i, ponto_externo_2d in enumerate(pontos_quadrado):
            contornos_2d = gerarContornosEntreVaraEQuadrado(
                (centro_x, centro_y),
                ponto_externo_2d,
                raio_vara,
                camadas_deformadas,
                razao_ballooning,
            )

            for camada, ponto_2d in enumerate(contornos_2d):
                ids_contornos[iz, camada, i] = adicionarPonto(
                    pontos,
                    mapa_pontos,
                    (ponto_2d[0], ponto_2d[1], z),
                )

    return ids_contornos


def gerarCubosEntreContornos(ids_contornos, camadas_deformadas):
    """
    Liga os pontos dos contornos para formar hexaedros deformados.
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


def gerarCubosDeformadosDaVara(
    pontos,
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
    Substitui o cubo normal por cubos deformados em volta da vara.
    """
    if raio_vara <= 0:
        raise ValueError("O raio da vara tem de ser positivo.")

    x_min = x_coords[intervalo_x_deformado[0]]
    x_max = x_coords[intervalo_x_deformado[1]]
    y_min = y_coords[intervalo_y_deformado[0]]
    y_max = y_coords[intervalo_y_deformado[1]]

    lado_menor = min(x_max - x_min, y_max - y_min)
    if raio_vara >= lado_menor / 2:
        raise ValueError("O raio da vara tem de ser menor que metade do lado do cubo deformado.")

    pontos_quadrado = gerarPontosDoQuadrado(x_min, x_max, y_min, y_max, divisoes_aresta)
    ids_contornos = gerarIdsDosContornosDaVara(
        pontos,
        mapa_pontos,
        z_coords,
        pontos_quadrado,
        centro_vara,
        raio_vara,
        camadas_deformadas,
        razao_ballooning,
    )

    return gerarCubosEntreContornos(ids_contornos, camadas_deformadas)


def gerarMalhaComVara(
    n_cubos_x,
    n_cubos_y,
    n_cubos_z,
    tamanho_total_x,
    tamanho_total_y,
    tamanho_total_z,
    cubo_deformado_x,
    cubo_deformado_y,
    raio_vara=RAIO_VARA,
    comprimento_vara=COMPRIMENTO_VARA,
    divisoes_cubo_deformado=DIVISOES_CUBO_DEFORMADO,
    divisoes_cubo_longe=DIVISOES_CUBO_LONGE,
    camadas_deformadas=CAMADAS_DEFORMADAS,
    razao_ballooning=RAZAO_BALLOONING,
):
    """
    Cria uma malha fixa e coloca a vara no centro do cubo escolhido.
    """
    if n_cubos_x < 1 or n_cubos_y < 1 or n_cubos_z < 1:
        raise ValueError("O numero de cubos tem de ser maior que zero.")

    if tamanho_total_x <= 0 or tamanho_total_y <= 0 or tamanho_total_z <= 0:
        raise ValueError("Os tamanhos totais da malha devem ser positivos.")

    if comprimento_vara <= 0:
        raise ValueError("O comprimento da vara tem de ser positivo.")

    if comprimento_vara > tamanho_total_z:
        raise ValueError("O comprimento da vara nao pode ser maior que a altura total da malha.")

    if divisoes_cubo_deformado < 2:
        raise ValueError("O cubo deformado precisa de pelo menos 2 divisoes por aresta.")

    if divisoes_cubo_longe < 1:
        raise ValueError("As divisoes dos cubos longe da vara devem ser pelo menos 1.")

    if divisoes_cubo_longe > divisoes_cubo_deformado:
        raise ValueError("As divisoes longe da vara nao podem ser maiores que as divisoes do cubo deformado.")

    if camadas_deformadas < 1:
        raise ValueError("O cubo deformado precisa de pelo menos 1 camada deformada.")

    if razao_ballooning < 1:
        raise ValueError("A razao de ballooning deve ser maior ou igual a 1.")

    cubo_deformado_x = limitarIndiceCubo(cubo_deformado_x, n_cubos_x, "cubo_deformado_x")
    cubo_deformado_y = limitarIndiceCubo(cubo_deformado_y, n_cubos_y, "cubo_deformado_y")
    cubo_deformado = (cubo_deformado_x, cubo_deformado_y)

    origem = (0.0, 0.0, 0.0)
    tamanho_cubo_x = tamanho_total_x / n_cubos_x
    tamanho_cubo_y = tamanho_total_y / n_cubos_y
    tamanho_cubo_z = tamanho_total_z / n_cubos_z
    z_fim_vara = tamanho_total_z
    z_inicio_vara = z_fim_vara - comprimento_vara

    centro_vara = calcularCentroDoCubo(
        origem,
        cubo_deformado_x,
        cubo_deformado_y,
        tamanho_cubo_x,
        tamanho_cubo_y,
    )

    divisoes_x_por_cubo = calcularDivisoesPorEixo(
        n_cubos_x,
        cubo_deformado_x,
        divisoes_cubo_deformado,
        divisoes_cubo_longe,
    )
    divisoes_y_por_cubo = calcularDivisoesPorEixo(
        n_cubos_y,
        cubo_deformado_y,
        divisoes_cubo_deformado,
        divisoes_cubo_longe,
    )
    divisoes_z_por_cubo_lista = calcularDivisoesZComVara(
        n_cubos_z,
        tamanho_cubo_z,
        z_inicio_vara,
        z_fim_vara,
        divisoes_cubo_deformado,
        divisoes_cubo_longe,
    )

    x_coords, intervalos_x = gerarCoordenadasPorCubo(n_cubos_x, tamanho_cubo_x, divisoes_x_por_cubo, origem[0])
    y_coords, intervalos_y = gerarCoordenadasPorCubo(n_cubos_y, tamanho_cubo_y, divisoes_y_por_cubo, origem[1])
    z_coords, intervalos_z = gerarCoordenadasPorCubo(n_cubos_z, tamanho_cubo_z, divisoes_z_por_cubo_lista, origem[2])
    z_coords = adicionarCoordenadaObrigatoria(z_coords, z_inicio_vara)
    z_coords = adicionarCoordenadaObrigatoria(z_coords, z_fim_vara)
    z_coords_vara = z_coords[
        (z_coords >= z_inicio_vara - 1e-12)
        & (z_coords <= z_fim_vara + 1e-12)
    ]

    pontos_base = gerarPontosOrdenados(x_coords, y_coords, z_coords)
    pontos = [tuple(ponto) for ponto in pontos_base]
    mapa_pontos = gerarMapaPontos(pontos_base)

    quantidade_pontos_y = len(y_coords)
    quantidade_pontos_z = len(z_coords)

    cubos_normais = gerarCubosNormais(
        intervalos_x,
        intervalos_y,
        z_coords,
        cubo_deformado,
        z_inicio_vara,
        z_fim_vara,
        quantidade_pontos_y,
        quantidade_pontos_z,
    )

    cubos_deformados = gerarCubosDeformadosDaVara(
        pontos,
        mapa_pontos,
        x_coords,
        y_coords,
        z_coords_vara,
        intervalos_x[cubo_deformado_x],
        intervalos_y[cubo_deformado_y],
        centro_vara,
        raio_vara,
        divisoes_cubo_deformado,
        camadas_deformadas,
        razao_ballooning,
    )

    pontos = np.asarray(pontos, dtype=float)
    cubos = np.asarray(cubos_normais + cubos_deformados, dtype=int)

    informacao = {
        "origem": origem,
        "limites": (
            origem[0],
            origem[0] + tamanho_total_x,
            origem[1],
            origem[1] + tamanho_total_y,
            origem[2],
            origem[2] + tamanho_total_z,
        ),
        "cubo_deformado": cubo_deformado,
        "centro_vara": centro_vara,
        "raio_vara": raio_vara,
        "comprimento_vara": comprimento_vara,
        "z_inicio_vara": z_inicio_vara,
        "z_fim_vara": z_fim_vara,
        "tamanho_total": (tamanho_total_x, tamanho_total_y, tamanho_total_z),
        "tamanho_cubo": (tamanho_cubo_x, tamanho_cubo_y, tamanho_cubo_z),
        "divisoes_x_por_cubo": divisoes_x_por_cubo,
        "divisoes_y_por_cubo": divisoes_y_por_cubo,
        "divisoes_z_por_cubo": divisoes_z_por_cubo_lista,
        "divisoes_cubo_deformado": divisoes_cubo_deformado,
        "camadas_deformadas": camadas_deformadas,
        "razao_ballooning": razao_ballooning,
        "cubos_normais": len(cubos_normais),
        "cubos_deformados": len(cubos_deformados),
        "intervalos_z": intervalos_z,
        "intervalos_z_vara": len(z_coords_vara) - 1,
        "z_coords": z_coords,
        "z_coords_vara": z_coords_vara,
    }

    return pontos, cubos, informacao


def divCubesInTetraedros(cube_list,pontos):
    c = 0
    # print(cubo.shape)
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
        ids = tetraedro[i, 1:5] # indice dos 4 pontos do tetraedro da posiçao I

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

    #print("min volume:", min(volumes))
    #print("max volume:", max(volumes))
    #print("volumes negativos:", np.sum(np.array(volumes) < 0))
    #print("volumes zero:", np.sum(np.abs(volumes) < 1e-12))
    return tetraedro





def criarGridPyVista(pontos, tetra):
    import pyvista as pv
    from pyvista import CellType

    tipos = np.full(len(tetra), CellType.TETRA, dtype=np.uint8)
    return pv.UnstructuredGrid(tetra.ravel(), tipos, pontos)


def validarMalha(pontos, cubos):
    if len(pontos) == 0:
        raise AssertionError("A malha nao tem pontos.")

    if len(cubos) == 0:
        raise AssertionError("A malha nao tem elementos.")

    if cubos[:, 0].min() != 8 or cubos[:, 0].max() != 8:
        raise AssertionError("Todos os elementos devem ser hexaedros com 8 vertices.")

    ids = cubos[:, 1:]
    if ids.min() < 0:
        raise AssertionError("Existem indices negativos nos elementos.")

    if ids.max() >= len(pontos):
        raise AssertionError("Existem elementos a apontar para pontos inexistentes.")


def validarMalhaComPyVista(pontos, tetra):
    grid = criarGridPyVista(pontos, tetra)
    volumes = grid.compute_cell_sizes(length=False, area=False, volume=True)["Volume"]

    superficie = grid.extract_surface(algorithm="dataset_surface")
    arestas_abertas = superficie.extract_feature_edges(
        boundary_edges=True,
        feature_edges=False,
        manifold_edges=False,
        non_manifold_edges=False,
    )

    return {
        "volume_minimo": float(volumes.min()),
        "volumes_nulos": int(np.sum(np.isclose(volumes, 0))),
        "volumes_negativos": int(np.sum(volumes < 0)),
        "arestas_abertas": int(arestas_abertas.n_cells),
    }


def mostrarMalha(pontos, tetra, informacao):
    import pyvista as pv

    grid = criarGridPyVista(pontos, tetra)
    validacao = validarMalhaComPyVista(pontos, tetra)

    print("Volume minimo:", validacao["volume_minimo"])
    print("Volumes nulos:", validacao["volumes_nulos"])
    print("Volumes negativos:", validacao["volumes_negativos"])
    print("Arestas abertas:", validacao["arestas_abertas"])

    z_min = informacao["z_inicio_vara"]
    z_max = informacao["z_fim_vara"]
    altura_vara = z_max - z_min
    centro_z = (z_min + z_max) / 2

    vara = pv.Cylinder(
        center=(informacao["centro_vara"][0], informacao["centro_vara"][1], centro_z),
        direction=(0, 0, 1),
        radius=informacao["raio_vara"],
        height=altura_vara,
        resolution=32,
    )

    plotter = pv.Plotter()
    plotter.add_mesh(grid, color="lightgray", show_edges=True, opacity=0.75)
    plotter.add_mesh(vara, color="red", opacity=1.0)
    plotter.add_axes()
    plotter.show()


def imprimirInformacao(pontos, cubos, informacao):
    print("\nInformacao da malha")
    print("===================")
    print("Limites:", informacao["limites"])
    print("Cubo deformado:", informacao["cubo_deformado"])
    print("Centro da vara:", informacao["centro_vara"])
    print("Raio da vara:", informacao["raio_vara"])
    print("Comprimento da vara:", informacao["comprimento_vara"])
    print("Intervalo Z da vara:", (informacao["z_inicio_vara"], informacao["z_fim_vara"]))
    print("Tamanho total da malha:", informacao["tamanho_total"])
    print("Tamanho de cada cubo base:", informacao["tamanho_cubo"])
    print("Divisoes em X por cubo:", informacao["divisoes_x_por_cubo"])
    print("Divisoes em Y por cubo:", informacao["divisoes_y_por_cubo"])
    print("Divisoes em Z por cubo:", informacao["divisoes_z_por_cubo"])
    print("Camadas deformadas no cubo da vara:", informacao["camadas_deformadas"])
    print("Razao de ballooning:", informacao["razao_ballooning"])
    print("Numero de pontos:", len(pontos))
    print("Cubos normais:", informacao["cubos_normais"])
    print("Cubos deformados:", informacao["cubos_deformados"])
    print("Numero total de elementos:", len(cubos))


def correrTestesRapidos():
    pontos, cubos, informacao = gerarMalhaComVara(
        n_cubos_x=4,
        n_cubos_y=4,
        n_cubos_z=5,
        tamanho_total_x=4.0,
        tamanho_total_y=4.0,
        tamanho_total_z=5.0,
        cubo_deformado_x=1,
        cubo_deformado_y=2,
    )

    validarMalha(pontos, cubos)

    assert informacao["centro_vara"] == (1.5, 2.5)
    assert informacao["divisoes_x_por_cubo"][1] == 4
    assert informacao["divisoes_y_por_cubo"][2] == 4
    assert np.isclose(informacao["z_fim_vara"], 5.0)
    assert np.isclose(informacao["z_inicio_vara"], 1.7)
    assert informacao["cubos_normais"] > 0
    lados_contorno = 4 * informacao["divisoes_cubo_deformado"]
    cubos_deformados_esperados = informacao["camadas_deformadas"] * lados_contorno * informacao["intervalos_z_vara"]
    assert informacao["cubos_deformados"] == cubos_deformados_esperados

    try:
        validacao = validarMalhaComPyVista(pontos, cubos)
    except ImportError:
        print("PyVista nao esta instalado; foram executados apenas os testes numericos.")
    else:
        assert validacao["volumes_nulos"] == 0
        assert validacao["volumes_negativos"] == 0
        print("Validacao PyVista:", validacao)

    print("Testes rapidos OK.")


def lerValor(mensagem, tipo):
    return tipo(input(mensagem))


def correrModoInterativo():
    n_cubos_x = lerValor("Numero de cubos base em X: ", int)
    n_cubos_y = lerValor("Numero de cubos base em Y: ", int)
    n_cubos_z = lerValor("Numero de cubos base em Z: ", int)
    tamanho_total_x = lerValor("Tamanho total da malha em X: ", float)
    tamanho_total_y = lerValor("Tamanho total da malha em Y: ", float)
    tamanho_total_z = lerValor("Tamanho total da malha em Z: ", float)
    cubo_deformado_x = lerValor("Indice X do cubo que recebe a vara: ", int)
    cubo_deformado_y = lerValor("Indice Y do cubo que recebe a vara: ", int)

    pontos, cubos, informacao = gerarMalhaComVara(
        n_cubos_x,
        n_cubos_y,
        n_cubos_z,
        tamanho_total_x,
        tamanho_total_y,
        tamanho_total_z,
        cubo_deformado_x,
        cubo_deformado_y,
    )
    tetra=divCubesInTetraedros(cubos,pontos)
    validarMalha(pontos, cubos)
    imprimirInformacao(pontos, cubos, informacao)
    mostrarMalha(pontos, tetra, informacao)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="corre validacoes rapidas sem pedir input")
    args = parser.parse_args()

    if args.test:
        correrTestesRapidos()
    else:
        correrModoInterativo()


if __name__ == "__main__":
    main()
