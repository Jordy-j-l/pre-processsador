import numpy as np
import pyvista as pv
from numpy.ma.core import append
from pyvista import CellType


dx=2
dy=2
dz=2

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


def divCubesInTetraedros(nx,ny,nz):
    c=0
    cubo=gerarCubos(nx,ny,nz)
    print(cubo.shape)
    tetraedro=np.empty(((len(cubo)*5),5),dtype=int)
    print(tetraedro.shape)
    for i in range(len(cubo)):
        tetraedro[c] = [4, cubo[i, 1], cubo[i, 2], cubo[i, 4], cubo[i, 5]]
        tetraedro[c+1] = [4, cubo[i, 2], cubo[i, 3], cubo[i, 4], cubo[i, 7]]
        tetraedro[c+2] = [4, cubo[i, 2], cubo[i, 4], cubo[i, 5], cubo[i, 7]]
        tetraedro[c+3] = [4, cubo[i, 2], cubo[i, 5], cubo[i, 6], cubo[i, 7]]
        tetraedro[c+4] = [4, cubo[i, 4], cubo[i, 5], cubo[i, 7], cubo[i, 8]]
        c+=5
    return tetraedro

print(divCubesInTetraedros(dx,dy,dz))



points = gerarPoints(dx,dy,dz)



"""
cube = np.array([
    [8, (z+y*(dz+1)+x*(dz+1)*(dy+1)), (z+y*(dz+1)+(x+1)*(dz+1)*(dy+1)), ((z+1)+y*(dz+1)+(x+1)*(dz+1)*(dy+1)), ((z+1)+y*(dz+1)+x*(dz+1)*(dy+1)),(z+(y+1)*(dz+1)+x*(dz+1)*(dy+1)), (z+(y+1)*(dz+1)+(x+1)*(dz+1)*(dy+1)), ((z+1)+(y+1)*(dz+1)+(x+1)*(dz+1)*(dy+1)), ((z+1)+(y+1)*(dz+1)+x*(dz+1)*(dy+1))],
])
"""


cube = gerarCubos(dx,dy,dz)




type = np.array([CellType.HEXAHEDRON]*len(cube))

tetraedro =divCubesInTetraedros(dx,dy,dz)
typet = np.array([CellType.TETRA]*len(tetraedro))





pl=pv.Plotter()
cloud=pv.PolyData(points)
pl.add_mesh(cloud,color="red",opacity=0)

grid = pv.UnstructuredGrid(cube.ravel(), type, points)

pl.add_mesh(grid,color="blue",opacity=0,show_edges=True)
gridt=pv.UnstructuredGrid(tetraedro, typet, points)
pl.add_mesh(gridt,color="green",opacity=0.5,show_edges=True)
pl.show()
