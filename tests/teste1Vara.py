import numpy as np
import pyvista as pv
from Demos.SystemParametersInfo import new_y
from pyvista import CellType

"""
raio = 0.00794
comprimento = 3.3
n_lados = 12
n_z = 20

theta = np.linspace(0, 2 * np.pi, n_lados, endpoint=False)
z_coords = np.linspace(0, -comprimento, n_z + 1)

points = []

for z in z_coords:
    for ang in theta:
        x = raio * np.cos(ang)
        y = raio * np.sin(ang)
        points.append([x, y, z])
for z in z_coords:
    for ang in theta:
        x = (raio * np.cos(ang))+1
        y = raio * np.sin(ang)
        points.append([x, y, z])

points = np.array(points, dtype=float)


faces = np.empty((n_z * n_lados*2, 9), dtype=int)

c = 0

for k in range(n_z):
    for i in range(n_lados):
        j = (i + 1) % n_lados

        p0 = k * n_lados + i
        p1 = (n_z * n_lados + i)+1
        p2 = ((k + 1) * n_lados + i)+((n_z * n_lados + i)+1)
        p3 = (k + 1) * n_lados + i
        p4 = k * n_lados + j
        p5 = (k * n_lados + j)+((n_z * n_lados + i)+1)
        p6 = ((k + 1) * n_lados + i)+(k * n_lados + j)+((n_z * n_lados + i)+1)
        p7 = (k + 1) * n_lados + j

        faces[c] = [8, p0, p1, p2,p3,p4,p5,p6,p7]
        c += 1


cell_types = np.array([CellType.HEXAHEDRON] * len(faces))

cilindro = pv.UnstructuredGrid(
    faces.ravel(),
    cell_types,
    points
)



def gerarCubos(nx,ny,nz):

    os pontos iniciais paracriação de qualquer cubo tem de cumprir a seguinte regra
    x < dx
    y < dy
    z < dz
   
   
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
plotter = pv.Plotter()
plotter.add_mesh(cilindro, color="gray", show_edges=True)
plotter.add_axes()
plotter.show()
"""

import numpy as np
import pyvista as pv
from pyvista import CellType


raio_interno = 0.00794
a =(raio_interno*2)  #metade de um lado do cubo desejado
comprimento = 3.3
n_lados = 24
n_z = 20
n_y=2
n_x=2

theta = np.linspace(0, 2 * np.pi, n_lados, endpoint=False)
z_coords = np.linspace(0, -comprimento, n_z + 1)

points = []

# Anel interno
for z in z_coords:
    for ang in theta:
        x = raio_interno * np.cos(ang)
        y = raio_interno * np.sin(ang)
        points.append([x, y, z])

# Anel externo

#calcular o vetor entre o pint ao ponto externo desejado


for z in z_coords:
        for ang in theta:
            t = a / max(abs(np.cos(ang)), abs(np.sin(ang)))
            x = t*np.cos(ang)
            y = t * np.sin(ang)
            points.append([x, y, z])




points = np.array(points, dtype=float)


offset = (n_z + 1) * n_lados

hexas = np.empty((n_z * n_lados, 9), dtype=int)

c = 0

for k in range(n_z):
    for i in range(n_lados):
        j = (i + 1) % n_lados

        # camada k
        p0 = k * n_lados + i
        p1 = k * n_lados + j
        p2 = offset + k * n_lados + j
        p3 = offset + k * n_lados + i

        # camada k+1
        p4 = (k + 1) * n_lados + i
        p5 = (k + 1) * n_lados + j
        p6 = offset + (k + 1) * n_lados + j
        p7 = offset + (k + 1) * n_lados + i

        hexas[c] = [8, p0, p1, p2, p3, p4, p5, p6, p7]
        c += 1

cell_types = np.array([CellType.HEXAHEDRON] * len(hexas))

grid = pv.UnstructuredGrid(
    hexas.ravel(),
    cell_types,
    points
)

plotter = pv.Plotter()
plotter.add_mesh(grid, color="gray", show_edges=True, opacity=0.8)
plotter.add_axes()
plotter.show()