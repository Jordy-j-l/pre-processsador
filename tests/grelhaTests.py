import numpy as np
import pyvista as pv
from numpy.ma.core import append
from pyvista import CellType


dx=2
dy=2
dz=1
front="x"

def gerarPoints(nx,ny,nz):
    points = np.empty(((nx+1)*(ny+1)*(nz+1),3))
    i=0
    for x in range(nx+1):
        for y in range(ny+1):
            for z in range(nz+1):
                points[i][0] = x
                points[i][1] = y
                points[i][2] = z
                i+=1

    return points

def gerarCubos(nx,ny,nz):
    """
    os pontos iniciais paracriação de qualquer cubo tem de cumprir a seguinte regra
    x < nx
    y < ny
    z < nz
    """
    cubelist=np.empty((nx*ny*nz,9),dtype=int)

    spoints=np.empty((nx*ny*nz,3),dtype=int)

    i = 0
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                spoints[i][0] = x
                spoints[i][1] = y
                spoints[i][2] = z
                i += 1

    for e in range(nx*ny*nz):
        x=spoints[e][0]
        y=spoints[e][1]
        z=spoints[e][2]
        cubelist[e][0] = 8
        cubelist[e][1] =(z+y*(nz+1)+x*(nz+1)*(ny+1))
        cubelist[e][2] = (z+y*(nz+1)+(x+1)*(nz+1)*(ny+1))
        cubelist[e][3] = ((z+1)+y*(nz+1)+(x+1)*(nz+1)*(ny+1))
        cubelist[e][4] =  ((z+1)+y*(nz+1)+x*(nz+1)*(ny+1))
        cubelist[e][5] = (z+(y+1)*(nz+1)+x*(nz+1)*(ny+1))
        cubelist[e][6] = (z+(y+1)*(nz+1)+(x+1)*(nz+1)*(ny+1))
        cubelist[e][7] =((z+1)+(y+1)*(nz+1)+(x+1)*(nz+1)*(ny+1))
        cubelist[e][8] = ((z+1)+(y+1)*(nz+1)+x*(nz+1)*(ny+1))
    return cubelist


def divCubesInTetraedros(nx,ny,nz,cubo):
    c=0
    #print(cubo.shape)
    tetraedro=np.empty(((len(cubo)*5),5),dtype=int)
    #print(tetraedro.shape)
    for i in range(len(cubo)):
        tetraedro[c] = [4, cubo[i, 1], cubo[i, 2], cubo[i, 4], cubo[i, 5]]
        tetraedro[c+1] = [4, cubo[i, 2], cubo[i, 3], cubo[i, 4], cubo[i, 7]]
        tetraedro[c+2] = [4, cubo[i, 2], cubo[i, 4], cubo[i, 5], cubo[i, 7]]
        tetraedro[c+3] = [4, cubo[i, 2], cubo[i, 5], cubo[i, 6], cubo[i, 7]]
        tetraedro[c+4] = [4, cubo[i, 4], cubo[i, 5], cubo[i, 7], cubo[i, 8]]
        c+=5
    return tetraedro
def reorganizar (pontos,dx,dy,dz,front,cubos):

    newpoints=np.empty((pontos.shape),dtype=float)


    fronts=0
    frontI=0
    frontLat=0
    frontLivre=0

    for i in range(len(pontos)):

        if front == "x":
            if pontos[i][0] == dx:
                fronts += 1
                #print("ponto de fronteira superior")
            elif pontos[i][0] == 0:
                frontI+=1
                #print("ponto de fronteira inferior")
            elif (pontos[i][0] != dx and pontos[i][0] != 0) and ((pontos[i][1] == dy or pontos[i][1] == 0) or (pontos[i][2] == dz or pontos[i][2] == 0)):
                frontLat+=1
                #print("ponto de fronteira lateral")
            elif pontos[i][0]!=dx and pontos[i][1]!=dy and pontos[i][2]!=dz and pontos[i][0] != 0 and pontos[i][1] != 0 and pontos[i][2] != 0:
                frontLivre+=1
                #print("pontos livres")
        elif front=="y":
            if (pontos[i][1] != dy and pontos[i][1] != 0) and ((pontos[i][0] == dx or pontos[i][0] == 0) or (pontos[i][2] == dz or pontos[i][2] == 0)):
                frontLat += 1
                #print("ponto de fronteira lateral")
            elif pontos[i][0] != dx and pontos[i][1] != dy and pontos[i][2] != dz and pontos[i][0] != 0 and pontos[i][1] != 0 and pontos[i][2] != 0:
                frontLivre += 1
                #print("pontos livres")
            elif pontos[i][1] == dy:
                fronts += 1
                #print("ponto de fronteira superior")
            elif pontos[i][1] == 0:
                frontI += 1
                #print("ponto de fronteira inferior")

        elif front=="z":
            if pontos[i][2]==dz:
                fronts += 1
                #print("ponto de fronteira superior")
            elif pontos[i][2] == 0:
                frontI += 1
                #print("ponto de fronteira inferior")
            elif (pontos[i][2] != dz and pontos[i][2] != 0) and (
                    (pontos[i][1] == dy or pontos[i][1] == 0) or (pontos[i][0] == dx or pontos[i][0] == 0)):
                frontLat += 1
                #print("ponto de fronteira lateral")
            elif pontos[i][0] != dx and pontos[i][1] != dy and pontos[i][2] != dz and pontos[i][0] != 0 and pontos[i][
                1] != 0 and pontos[i][2] != 0:
                frontLivre += 1
                #print("pontos livres")



    vetorFinal=np.array([frontLivre+frontLat,fronts,frontI])
    mapa = np.empty(len(pontos), dtype=int)
    novoid=0
    #print("Pontos =================")
    #print(frontLivre, frontLat, fronts, frontI)
    #print("Vetor", vetorFinal)
    #print("========================")
    #print(vetorFinal)
    #print(len(pontos))
    #Livre
    for i in range(len(pontos)):
    #    print(novoid)
        if front == "x":
            if pontos[i][0]!=dx and pontos[i][1]!=dy and pontos[i][2]!=dz and pontos[i][0] != 0 and pontos[i][1] != 0 and pontos[i][2] != 0:
                newpoints[novoid] = pontos[i]
                mapa[i] = novoid
                novoid += 1
        if front == "y":
            if pontos[i][0] != dx and pontos[i][1] != dy and pontos[i][2] != dz and pontos[i][0] != 0 and pontos[i][1] != 0 and pontos[i][2] != 0:
                newpoints[novoid] = pontos[i]
                mapa[i] = novoid
                novoid += 1
        if front == "z":
            if pontos[i][0] != dx and pontos[i][1] != dy and pontos[i][2] != dz and pontos[i][0] != 0 and pontos[i][
                1] != 0 and pontos[i][2] != 0:
                newpoints[novoid] = pontos[i]
                mapa[i] = novoid
                novoid += 1
#Fronteira Lateral
    for i in range(len(pontos)):
     #   print(novoid)
        if front == "x":
            if (pontos[i][0] != dx and pontos[i][0] != 0) and ((pontos[i][2] == dz or pontos[i][2] == 0) or (pontos[i][1] == dy or pontos[i][1] == 0)):
                 newpoints[novoid] = pontos[i]
                 mapa[i] = novoid
                 novoid += 1
        if front == "y":
            if (pontos[i][1] != dy and pontos[i][1] != 0) and ((pontos[i][2] == dz or pontos[i][2] == 0) or (pontos[i][0] == dx or pontos[i][0] == 0)):
                newpoints[novoid] = pontos[i]
                mapa[i] = novoid
                novoid += 1
        if front == "z":
            if (pontos[i][2] != dz and pontos[i][2] != 0) and ((pontos[i][1] == dy or pontos[i][1] == 0) or (pontos[i][0] == dx or pontos[i][0] == 0)):
                (newpoints)[novoid] = pontos[i]
                mapa[i] = novoid
                novoid += 1

                #Fronteira Superior
    for i in range(len(pontos)):
      #  print(novoid)
        if front == "x":
            if pontos[i][0] == dx:
                newpoints[novoid] = pontos[i]
                mapa[i] = novoid
                novoid += 1
        if front == "y":
            if pontos[i][1] == dy:
                newpoints[novoid] = pontos[i]
                mapa[i] = novoid
                novoid += 1
        if front == "z":
            if pontos[i][2] == dz:
                newpoints[novoid] = pontos[i]
                mapa[i] = novoid
                novoid += 1
                #Fronteira Inferior
    for i in range(len(pontos)):
       # print(novoid)
        if front == "x":
            if pontos[i][0] == 0:
                newpoints[novoid] = pontos[i]
                mapa[i] = novoid
                novoid += 1
        if front == "y":
            if pontos[i][1] == 0:
                newpoints[novoid] = pontos[i]
                mapa[i] = novoid
                novoid += 1
        if front == "z":
            if pontos[i][2] == 0:
                newpoints[novoid] = pontos[i]
                mapa[i] = novoid
                novoid += 1



    """
    if front == "x":
        if pontos[i][0] == dx:
        elif pontos[i][0] == 0:
        elif (pontos[i][0] != dx and pontos[i][0] != 0) and (
                (pontos[i][1] == dy or pontos[i][1] == 0) or (pontos[i][2] == dz or pontos[i][2] == 0)):
            
        elif pontos[i][0] != dx and pontos[i][1] != dy and pontos[i][2] != dz and pontos[i][0] != 0 and pontos[i][
            1] != 0 and pontos[i][2] != 0:
               
    elif front == "y":
        if pontos[i][1] == dy:
                newpoints[novoid] = pontos[i]
                mapa[i] = novoid
                fronts -= 1
                novoid += 1
        elif pontos[i][1] == 0:
                newpoints[novoid] = pontos[i]
                mapa[i] = novoid
                novoid += 1
        elif (pontos[i][1] != dy and pontos[i][1] != 0) and (
                (pontos[i][0] == dx or pontos[i][0] == 0) or (pontos[i][2] == dz or pontos[i][2] == 0)):
           
                newpoints[novoid] = pontos[i]

                mapa[i] = novoid
                
                novoid += 1
        elif pontos[i][0] != dx and pontos[i][1] != dy and pontos[i][2] != dz and pontos[i][0] != 0 and pontos[i][
            1] != 0 and pontos[i][2] != 0:
            
                
    elif front == "z":
        if pontos[i][2] == dz:
           
                newpoints[novoid] = pontos[i]

                mapa[i] = novoid
                novoid += 1
               
        elif pontos[i][2] == 0:
           
                newpoints[novoid] = pontos[i]

                mapa[i] = novoid
                novoid += 1
               
        elif (pontos[i][2] != dz and pontos[i][2] != 0) and (
                (pontos[i][1] == dy or pontos[i][1] == 0) or (pontos[i][0] == dx or pontos[i][0] == 0)):

    for i in range(len(pontos)):
        print(novoid)
        if front == "x":
            if pontos[i][0] == dx:
              
                   newpoints[novoid]= pontos[i]


                   mapa[i]=novoid
                   fronts-=1
                   novoid+=1
            elif pontos[i][0] == 0:
                if (frontLivre == 0 and frontLat == 0 and fronts==0):
                    newpoints[novoid]= pontos[i]

                    mapa[i]=novoid
                    frontI -= 1
                    novoid += 1
            elif (pontos[i][0] != dx and pontos[i][0] != 0) and ((pontos[i][1] == dy or pontos[i][1] == 0) or (pontos[i][2] == dz or pontos[i][2] == 0)):
                if (frontLivre == 0):
                    newpoints[novoid] = pontos[i]
                    mapa[i]=novoid

                    frontLat -= 1
                    novoid += 1
            elif pontos[i][0]!=dx and pontos[i][1]!=dy and pontos[i][2]!=dz and pontos[i][0] != 0 and pontos[i][1] != 0 and pontos[i][2] != 0:
                if (frontLivre != 0 and fronts != 0 and frontI != 0):
                    newpoints[novoid]= pontos[i]

                    mapa[i]=novoid
                    frontLivre -= 1
                    novoid += 1
        elif front=="y":
            if pontos[i][1] == dy:
                if (frontLivre == 0 and frontLat == 0):
                    newpoints[novoid]= pontos[i]

                    mapa[i]=novoid
                    fronts -= 1
                    novoid += 1
            elif pontos[i][1] == 0:
                if (frontLivre == 0 and frontLat == 0 and fronts == 0):
                    newpoints[novoid]= pontos[i]

                    mapa[i]=novoid
                    frontI -= 1
                    novoid += 1
            elif (pontos[i][1] != dy and pontos[i][1] != 0) and ((pontos[i][0] == dx or pontos[i][0] == 0) or (pontos[i][2] == dz or pontos[i][2] == 0)):
                if (frontLivre == 0):
                    newpoints[novoid]= pontos[i]

                    mapa[i]=novoid
                    frontLat -= 1
                    novoid += 1
            elif pontos[i][0] != dx and pontos[i][1] != dy and pontos[i][2] != dz and pontos[i][0] != 0 and pontos[i][
                1] != 0 and pontos[i][2] != 0:
                if (frontLivre != 0 and fronts != 0 and frontI != 0):
                    newpoints[novoid]= pontos[i]

                    mapa[i]=novoid
                    frontLivre -= 1
                    novoid += 1
        elif front=="z":
            if pontos[i][2]==dz:
                if (frontLivre == 0 and frontLat == 0):
                    newpoints[novoid]= pontos[i]

                    mapa[i]=novoid
                    novoid += 1
                    fronts -= 1
            elif pontos[i][2] == 0:
                if (frontLivre == 0 and frontLat == 0 and fronts == 0):
                    newpoints[novoid]= pontos[i]

                    mapa[i]=novoid
                    novoid += 1
                    frontI -= 1
            elif (pontos[i][2] != dz and pontos[i][2] != 0) and (
                    (pontos[i][1] == dy or pontos[i][1] == 0) or (pontos[i][0] == dx or pontos[i][0] == 0)):
                if (frontLivre == 0):
                    newpoints[novoid]= pontos[i]

                    mapa[i]=novoid
                    novoid += 1
                    frontLat -= 1
            elif pontos[i][0] != dx and pontos[i][1] != dy and pontos[i][2] != dz and pontos[i][0] != 0 and pontos[i][
                1] != 0 and pontos[i][2] != 0:
                if (frontLivre != 0 and fronts !=0 and frontI !=0):
                    newpoints[novoid]= pontos[i]

                    mapa[i]=novoid
                    frontLivre -= 1
                    novoid += 1
                    """
    #print("MAPA:", mapa)
    newcube=reordenarCubos(cubos,mapa)
    return vetorFinal,newcube,newpoints


def reordenarCubos(cubos,mapa):


    newcube=np.empty((cubos.shape),dtype=int)
    for i in range(len(cubos)):
        newcube[i][0] = 8
        newcube[i][1] = mapa[cubos[i][1]]
        newcube[i][2] = mapa[cubos[i][2]]
        newcube[i][3] = mapa[cubos[i][3]]
        newcube[i][4] = mapa[cubos[i][4]]
        newcube[i][5] = mapa[cubos[i][5]]
        newcube[i][6] = mapa[cubos[i][6]]
        newcube[i][7] =mapa[cubos[i][7]]
        newcube[i][8] = mapa[cubos[i][8]]
        """
         newcube[i][1] = i if (x, y, z) == newpoints[i] else cubos[i][1]
        newcube[i][2] = i if (x + 1, y, z) == newpoints[i] else cubos[i][1]
        newcube[i][3] = i if (x + 1, y, z + 1) == newpoints[i] else cubos[i][1]
        newcube[i][4] = i if (x, y, z + 1) == newpoints[i] else cubos[i][1]
        newcube[i][5] = i if (x, y + 1, z) == newpoints[i] else cubos[i][1]
        newcube[i][6] = i if (x + 1, y + 1, z) == newpoints[i] else cubos[i][1]
        newcube[i][7] = i if (x + 1, y + 1, z + 1) == newpoints[i] else cubos[i][1]
        newcube[i][8] = i if (x, y + 1, z + 1) == newpoints[i] else cubos[i][1]
        """


    return newcube






points = gerarPoints(dx,dy,dz)



"""
cube = np.array([
    [8, (z+y*(dz+1)+x*(dz+1)*(dy+1)), (z+y*(dz+1)+(x+1)*(dz+1)*(dy+1)), ((z+1)+y*(dz+1)+(x+1)*(dz+1)*(dy+1)), ((z+1)+y*(dz+1)+x*(dz+1)*(dy+1)),(z+(y+1)*(dz+1)+x*(dz+1)*(dy+1)), (z+(y+1)*(dz+1)+(x+1)*(dz+1)*(dy+1)), ((z+1)+(y+1)*(dz+1)+(x+1)*(dz+1)*(dy+1)), ((z+1)+(y+1)*(dz+1)+x*(dz+1)*(dy+1))],
])
"""


cube = gerarCubos(dx,dy,dz)


vetorfinal,cuboFinal,PontosFinal=reorganizar(points,dx,dy,dz,front,cube)

type = np.array([CellType.HEXAHEDRON]*len(cuboFinal))


tetraedro =divCubesInTetraedros(dx,dy,dz,cuboFinal)
typet = np.array([CellType.TETRA]*len(tetraedro))



#print("cubo final",cuboFinal)

#SHOW IN ECRÂ
cores_rgb = np.zeros((len(tetraedro), 3), dtype=np.uint8)
for i in range(len(tetraedro)):
    cores_rgb[i, 0] = np.random.randint(0, 256)
    cores_rgb[i, 1] =np.random.randint(0, 256)
    cores_rgb[i, 2] = np.random.randint(0, 256)
pl=pv.Plotter()

grid = pv.UnstructuredGrid(cuboFinal.ravel(), type, PontosFinal)

pl.add_mesh(grid,color="blue",opacity=0,show_edges=True)
gridt=pv.UnstructuredGrid(tetraedro, typet, PontosFinal)
gridt.cell_data["cores_rgb"]=cores_rgb
pl.add_mesh(gridt, scalars="cores_rgb",rgb=True,show_edges=True, opacity=0.1)
pl.show()


#exportar

exportp=np.empty((len(PontosFinal),4))
exporttetra=np.empty((len(tetraedro),5))
p=156#arresividade
for i in range(len(PontosFinal)):
    exportp[i][0]=PontosFinal[i][0]
    exportp[i][1]=PontosFinal[i][1]
    exportp[i][2]=PontosFinal[i][2]
    exportp[i][3]=-1 if i<vetorfinal[0] else 100 if i<vetorfinal[1]+vetorfinal[0] else 0
for i in range(len(tetraedro)):
    exporttetra[i,0]=tetraedro[i][1]
    exporttetra[i, 1] = tetraedro[i][2]
    exporttetra[i, 2] = tetraedro[i][3]
    exporttetra[i, 3] = tetraedro[i][4]
    exporttetra[i, 4] = p
#print("vetor final \n",vetorfinal)
#print(exportp)
print(tetraedro)
np.savetxt("pontos.txt", exportp, fmt="%.6f")
np.savetxt("elementos.txt", exporttetra, fmt="%d")
np.savetxt("Vetor.txt", vetorfinal, fmt="%d")