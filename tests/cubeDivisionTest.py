import numpy as np
import pyvista as pv
from pyvista import Cell, CellType

pontos=np.array([
    [0,0,0],
    [1,0,0],
    [1,0,1],
    [0,0,1],
    [0,1,0],
    [1,1,0],
    [1,1,1],
    [0,1,1],
])

cubo=np.array([[8,0,1,2,3,4,5,6,7]])
cubtype=np.array([CellType.HEXAHEDRON])
"""

tetraedros=np.array([
    [4,0, 1, 3, 4],  # T1  [4,cubo[0,1], cubo[0,2], cubo[0,4], cubo[0,5]], 
    [4,1, 2, 3, 6],  # T2   [4,cubo[0,2], cubo[0,3], cubo[0,4], cubo[0,7]], 
    [4,1, 3, 4, 6],  # T3 central  [4,cubo[0,2], cubo[0,4], cubo[0,5], cubo[0,7]], 
    [4,1, 4, 5, 6],  # T4   [4,cubo[0,2], cubo[0,5], cubo[0,6], cubo[0,7]], 
    [4,3, 4, 6, 7]   # T5    [4,cubo[0,4], cubo[0,5], cubo[0,7], cubo[0,8]], 
])
"""


tetraedros=np.array([
    [4,cubo[0,1], cubo[0,2], cubo[0,4], cubo[0,5]],
    [4,cubo[0,2], cubo[0,3], cubo[0,4], cubo[0,7]],
    [4,cubo[0,2], cubo[0,4], cubo[0,5], cubo[0,7]],
    [4,cubo[0,2], cubo[0,5], cubo[0,6], cubo[0,7]],
    [4,cubo[0,4], cubo[0,5], cubo[0,7], cubo[0,8]],
])
print(tetraedros.shape)

tetratype=np.array([CellType.TETRA])
tetratypes=np.array([CellType.TETRA]*len(tetraedros))
pl=pv.Plotter(shape=(2,3))



pl.subplot(0,0)
grid1=pv.UnstructuredGrid(tetraedros[0].ravel(),tetratype,pontos)
cub=pv.UnstructuredGrid(cubo.ravel(),cubtype,pontos)
pl.add_mesh(cub,color="white",opacity=0.1,show_edges=True)
pl.add_mesh(grid1,color="red",opacity=0.8)

pl.subplot(0,1)

grid2=pv.UnstructuredGrid(tetraedros[1].ravel(),tetratype,pontos)
pl.add_mesh(grid2,color="blue",opacity=0.7)
cub=pv.UnstructuredGrid(cubo.ravel(),cubtype,pontos)

pl.add_mesh(cub,color="white",opacity=0.1,show_edges=True)
pl.add_axes(
    xlabel="X",
    ylabel="Y",
    zlabel="Z",
    line_width=3,
    interactive=True
)
pl.subplot(0,2)
grid3=pv.UnstructuredGrid(tetraedros[2].ravel(),tetratype,pontos)
pl.add_mesh(grid3,color="green",opacity=1)
cub=pv.UnstructuredGrid(cubo.ravel(),cubtype,pontos)
pl.add_mesh(cub,color="white",opacity=0.1,show_edges=True)

pl.add_axes(
    xlabel="X",
    ylabel="Y",
    zlabel="Z",
    line_width=3,
    interactive=True
)
pl.subplot(1,0)
grid4=pv.UnstructuredGrid(tetraedros[3].ravel(),tetratype,pontos)
pl.add_mesh(grid4,color="yellow",opacity=0.7)
cub=pv.UnstructuredGrid(cubo.ravel(),cubtype,pontos)
pl.add_mesh(cub,color="white",opacity=0.1,show_edges=True)

pl.subplot(1,1)
grid5=pv.UnstructuredGrid(tetraedros[4].ravel(),tetratype,pontos)
pl.add_mesh(grid5,color="pink",opacity=0.7)
cub=pv.UnstructuredGrid(cubo.ravel(),cubtype,pontos)
pl.add_mesh(cub,color="white",opacity=0.1,show_edges=True)

pl.subplot(1,2)
pl.add_mesh(grid1,color="red",opacity=0.8)
pl.add_mesh(grid2,color="blue",opacity=0.8)
pl.add_mesh(grid3,color="green",opacity=0.8)
pl.add_mesh(grid4,color="yellow",opacity=0.8)
pl.add_mesh(grid5,color="pink",opacity=0.8)

pl.show()

