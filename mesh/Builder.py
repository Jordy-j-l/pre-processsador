import numpy as np

class Malha:

    def __init__(self, dx, dy, dz,sx=None,sy=None,sz=None,eixo_placas=None,vara_1=None,vara_2=None):

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
        # ====================================================================


        self.eixo_placas = eixo_placas # eixo onde fica situado as placas condensadas
        self.vara_1=vara_1
        self.vara_2=vara_2

        #=======================================================================
        self.cube_list=self.gerarCubos()
        self.points_list=self.gerarPointsOrdenados()
        self.final_cube_list,self.final_points_list=self.reorganizar()
        self.final_vector=self.gerarVetor()

    def gerarPointsOrdenados(self):

        #tamanho de cada espaçamento entre as divizoes feita
        ex = self.sx / self.dx
        ey = self.sy / self.dy
        ez = self.sz / self.dz

        points = np.empty(((self.dx + 1) * (self.dy + 1) * (self.dz + 1), 3))

        i = 0

        for x in range(self.dx + 1):
            for y in range(self.dy + 1):
                for z in range(self.dz + 1):
                    points[i][0] = x*ex
                    points[i][1] = y*ey
                    points[i][2] = z*ez
                    i += 1

        return points


    def gerarCubos(self):
        """
        os pontos iniciais paracriação de qualquer cubo tem de cumprir a seguinte regra
        x < nx
        y < ny
        z < nz
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

    ###################################################################################
    def isFronteiraSuperior(self,i):
        if self.eixo_placas == "x":
            if  self.points_list[i][0] == self.sx:
                return True
        elif self.eixo_placas == "y":
            if  self.points_list[i][1] == self.sy:
                return True
        else:
            if  self.points_list[i][2] == self.sz:
                return True
        return False
    def isFronteiraInferior(self,i):
        if self.eixo_placas == "x":
            if  self.points_list[i][0] == 0:
                return True
        elif self.eixo_placas == "y":
            if  self.points_list[i][1] == 0:
                return True
        else:
            if  self.points_list[i][2] == 0:
                return True
        return False

    def isFronteiratLateral(self,i):
        if self.eixo_placas == "x":
            if ( self.points_list[i][0] != self.sx and  self.points_list[i][0] != 0) and (( self.points_list[i][1] == self.sy or  self.points_list[i][1] == 0) or ( self.points_list[i][2] == self.sz or  self.points_list[i][2] == 0)):
                return True
        if self.eixo_placas == "y":
            if ( self.points_list[i][1] != self.sy and  self.points_list[i][1] != 0) and (
                    ( self.points_list[i][0] == self.sx or  self.points_list[i][0] == 0) or (
                     self.points_list[i][2] == self.sz or  self.points_list[i][2] == 0)):
                return True
        if self.eixo_placas == "z":
            if ( self.points_list[i][2] != self.sz and  self.points_list[i][2] != 0) and (
                    ( self.points_list[i][1] == self.sy or  self.points_list[i][1] == 0) or (
                     self.points_list[i][0] == self.sx or  self.points_list[i][0] == 0)):
                return True
        return False


    def isPontoLivre(self,i):
        if not self.isFronteiratLateral(i) and not self.isFronteiraInferior(i) and not self.isFronteiraSuperior(i):
            return True
        return False


    def gerarVetor(self):

        pontos =  self.points_list
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



    def reorganizar(self):

        cubos=self.cube_list
        pontos= self.points_list

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
        # print("MAPA:", mapa)
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
            #print(np.where(mapa == -1))
        #print("novoid:", novoid)
        #print("len pontos:", len(pontos))
        #print("maior indice cubos:", newcube[:, 1:].max())
        #print("menor indice cubos:", newcube[:, 1:].min())

        return newcube, newpoints


    def divCubesInTetraedros(self):
        cube_list=self.final_cube_list
        pontos = self.final_points_list
        c = 0
        # print(cubo.shape)
        tetraedro = np.empty(((len(cube_list) * 5), 5), dtype=int)
        # print(tetraedro.shape)
        for i in range(len(cube_list)):
            tetraedro[c] = [4, cube_list[i, 1], cube_list[i, 2], cube_list[i, 4], cube_list[i, 5]]
            tetraedro[c + 1] = [4, cube_list[i, 2], cube_list[i, 3], cube_list[i, 4], cube_list[i, 7]]
            tetraedro[c + 2] = [4, cube_list[i, 2], cube_list[i, 4], cube_list[i, 5], cube_list[i, 7]]
            tetraedro[c + 3] = [4, cube_list[i, 2], cube_list[i, 5], cube_list[i, 6], cube_list[i, 7]]
            tetraedro[c + 4] = [4, cube_list[i, 4], cube_list[i, 5], cube_list[i, 7], cube_list[i, 8]]
            c += 5

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

#Getters e Setters

    def getCubesList(self):
        return self.final_cube_list
    def getPointsList(self):
        return self.final_points_list
    def getTetraedrosList(self):
        return self.divCubesInTetraedros()
    def getVetorList(self):
        return self.final_vector

