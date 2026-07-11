def limitarIndiceCubo(cubo, numero_cubos, nome):

    if cubo < 0 or cubo >= numero_cubos:
        raise ValueError(f"{nome} tem de estar entre 0 e {numero_cubos - 1}.")

    return cubo
