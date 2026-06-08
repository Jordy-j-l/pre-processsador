import numpy as np


class Malha():

    def __init__(self, dx, dy, dz):
        self.dx = dx
        self.dy = dy
        self.dz = dz

    def gerarPoints(self):
        nx = self.dx
        ny = self.dy
        nz = self.dz
        points = np.empty(((nx + 1) * (ny + 1) * (nz + 1), 3))
        i = 0
        for x in range(nx + 1):
            for y in range(ny + 1):
                for z in range(nz + 1):
                    points[i][0] = x
                    points[i][1] = y
                    points[i][2] = z
                    i += 1

        return points


    def gerarCubos(self):
        """
        os pontos iniciais paracriação de qualquer cubo tem de cumprir a seguinte regra
        x < nx
        y < ny
        z < nz
        """
        nx=self.dx
        ny=self.dy
        nz=self.dz
        cubelist = np.empty((nx * ny * nz, 9), dtype=int)

        spoints = np.empty((nx * ny * nz, 3), dtype=int)

        i = 0
        for x in range(nx):
            for y in range(ny):
                for z in range(nz):
                    spoints[i][0] = x
                    spoints[i][1] = y
                    spoints[i][2] = z
                    i += 1

        for e in range(nx * ny * nz):
            x = spoints[e][0]
            y = spoints[e][1]
            z = spoints[e][2]
            cubelist[e][0] = 8
            cubelist[e][1] = (z + y * (nz + 1) + x * (nz + 1) * (ny + 1))
            cubelist[e][2] = (z + y * (nz + 1) + (x + 1) * (nz + 1) * (ny + 1))
            cubelist[e][3] = ((z + 1) + y * (nz + 1) + (x + 1) * (nz + 1) * (ny + 1))
            cubelist[e][4] = ((z + 1) + y * (nz + 1) + x * (nz + 1) * (ny + 1))
            cubelist[e][5] = (z + (y + 1) * (nz + 1) + x * (nz + 1) * (ny + 1))
            cubelist[e][6] = (z + (y + 1) * (nz + 1) + (x + 1) * (nz + 1) * (ny + 1))
            cubelist[e][7] = ((z + 1) + (y + 1) * (nz + 1) + (x + 1) * (nz + 1) * (ny + 1))
            cubelist[e][8] = ((z + 1) + (y + 1) * (nz + 1) + x * (nz + 1) * (ny + 1))

        #retorna a lista com os elementos do cubo
        return cubelist

    def divCubesInTetraedros(self):
        c = 0
        cubo = self.gerarCubos()
        print(cubo.shape)
        tetraedro = np.empty(((len(cubo) * 5), 5), dtype=int)
        print(tetraedro.shape)
        for i in range(len(cubo)):
            tetraedro[c] = [4, cubo[i, 1], cubo[i, 2], cubo[i, 4], cubo[i, 5]]
            tetraedro[c + 1] = [4, cubo[i, 2], cubo[i, 3], cubo[i, 4], cubo[i, 7]]
            tetraedro[c + 2] = [4, cubo[i, 2], cubo[i, 4], cubo[i, 5], cubo[i, 7]]
            tetraedro[c + 3] = [4, cubo[i, 2], cubo[i, 5], cubo[i, 6], cubo[i, 7]]
            tetraedro[c + 4] = [4, cubo[i, 4], cubo[i, 5], cubo[i, 7], cubo[i, 8]]
            c += 5
        return tetraedro