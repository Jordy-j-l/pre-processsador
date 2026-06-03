def list_ponto(lista):
    for i in range(len(lista)):
        print(f"Ponto {i}:{lista[i][0],lista[i][1],lista[i][2]}")


pontos = [
    [0,0,0],
    [1,0,0],
    [0.5,1,0],
    [0.5,0.5,1],
]

list_ponto(pontos)