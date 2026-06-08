import numpy as np
import pyvista as pv
from pyvista import CellType
from pyvista.core.utilities.cell_quality import TETRA

#pontos do cubo

cube_points = np.array([
    [0,0,0],#p1
    [1,0,0],#p2
    [1,1,0],#p3
    [0,1,0],#p4
    [0,0,1],#p5
    [1,0,1],#p6
    [1,1,1],#p7
    [0,1,1]#p8
],dtype=np.float64)

tetra = np.array([
    [4,0, 1, 3, 4],  # T1
    [4,1, 2, 3, 6],  # T2
    [4,1, 3, 4, 6],  # T3 central
    [4,1, 4, 5, 6],  # T4
    [4,3, 4, 6, 7]   # T5
])
cube=np.array([[8,0,1,2,3,4,5,6,7]])
print(len(cube))
tetratype = np.array([CellType.TETRA]*len(tetra))
cubetype= np.array([CellType.HEXAHEDRON]*len(cube))
pl=pv.Plotter(shape=(1,2))
pl.subplot(0,0)
cores_rgb = np.array([
    [0, 0, 0],    # Vermelho
    [0, 0, 0],    # Verde
    [0, 255, 0],    # Azul
    [0, 0, 0],  # Amarelo
    [0, 0, 0]   # Magenta
], dtype=np.uint8)  # Importante: usar uint8

grid = pv.UnstructuredGrid(tetra.ravel(), tetratype, cube_points)
grid.cell_data["cores_rgb"]=cores_rgb
pl.add_mesh(grid, scalars="cores_rgb",rgb=True,show_edges=True, opacity=0.1)
pl.subplot(0,1)
grid1 = pv.UnstructuredGrid(cube.ravel(), cubetype, cube_points)
pl.add_mesh(grid1, color="red",show_edges=True, opacity=1)
pl.show()


