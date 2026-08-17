import numpy as np
import pyvista as pv
import sys
from pathlib import Path
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
], dtype=float)

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
    [4,cubo[0,1], cubo[0,2], cubo[0,6], cubo[0,7]],
    [4,cubo[0,1], cubo[0,2], cubo[0,3], cubo[0,7]],
    [4,cubo[0,1], cubo[0,5], cubo[0,6], cubo[0,7]],
    [4,cubo[0,1], cubo[0,5], cubo[0,8], cubo[0,7]],
    [4,cubo[0,1], cubo[0,4], cubo[0,3], cubo[0,7]],
    [4,cubo[0,1], cubo[0,4], cubo[0,8], cubo[0,7]]
])

"""
tetraedro = np.empty(((len(cube_list) * 6), 5), dtype=int)

        for i in range(len(cube_list)):
            tetraedro[c] = [4, cube_list[i, 1], cube_list[i, 2], cube_list[i, 6], cube_list[i, 7]]
            tetraedro[c + 1] = [4, cube_list[i, 1], cube_list[i, 2], cube_list[i, 3], cube_list[i, 7]]
            tetraedro[c + 2] = [4, cube_list[i, 1], cube_list[i, 5], cube_list[i, 6], cube_list[i, 7]]
            tetraedro[c + 3] = [4, cube_list[i, 1], cube_list[i, 5], cube_list[i, 8], cube_list[i, 7]]
            tetraedro[c + 4] = [4, cube_list[i, 1], cube_list[i, 4], cube_list[i, 3], cube_list[i, 7]]
            tetraedro[c + 5] = [4, cube_list[i, 1], cube_list[i, 4], cube_list[i, 8], cube_list[i, 7]]
            c += 6
"""
print(tetraedros.shape)

tetratype=np.array([CellType.TETRA])
tetratypes=np.array([CellType.TETRA]*len(tetraedros))
modo_relatorio = "--report" in sys.argv
pl=pv.Plotter(shape=(2,3), off_screen=modo_relatorio, window_size=(1800, 1200))
pl.set_background("#f2f2f2", all_renderers=True)



pl.subplot(0,0)
grid1=pv.UnstructuredGrid(tetraedros[0].ravel(),tetratype,pontos)
cub=pv.UnstructuredGrid(cubo.ravel(),cubtype,pontos)
pl.add_mesh(cub,color="white",opacity=0.1,show_edges=True,edge_color="black")
pl.add_mesh(grid1,color="red",opacity=0.8,show_edges=True,edge_color="black",line_width=2)
pl.add_axes(
    xlabel="X",
    ylabel="Y",
    zlabel="Z",
    line_width=3,
    interactive=True
)
pl.subplot(0,1)

grid2=pv.UnstructuredGrid(tetraedros[1].ravel(),tetratype,pontos)
pl.add_mesh(grid2,color="blue",opacity=0.7,show_edges=True,edge_color="black",line_width=2)
cub=pv.UnstructuredGrid(cubo.ravel(),cubtype,pontos)

pl.add_mesh(cub,color="white",opacity=0.1,show_edges=True,edge_color="black")
pl.add_axes(
    xlabel="X",
    ylabel="Y",
    zlabel="Z",
    line_width=3,
    interactive=True
)
pl.subplot(0,2)
grid3=pv.UnstructuredGrid(tetraedros[2].ravel(),tetratype,pontos)
pl.add_mesh(grid3,color="green",opacity=1,show_edges=True,edge_color="black",line_width=2)
cub=pv.UnstructuredGrid(cubo.ravel(),cubtype,pontos)
pl.add_mesh(cub,color="white",opacity=0.1,show_edges=True,edge_color="black")

pl.add_axes(
    xlabel="X",
    ylabel="Y",
    zlabel="Z",
    line_width=3,
    interactive=True
)
pl.subplot(1,0)
grid4=pv.UnstructuredGrid(tetraedros[3].ravel(),tetratype,pontos)
pl.add_mesh(grid4,color="yellow",opacity=0.7,show_edges=True,edge_color="black",line_width=2)
cub=pv.UnstructuredGrid(cubo.ravel(),cubtype,pontos)
pl.add_mesh(cub,color="white",opacity=0.1,show_edges=True,edge_color="black")
pl.add_axes(
    xlabel="X",
    ylabel="Y",
    zlabel="Z",
    line_width=3,
    interactive=True
)
pl.subplot(1,1)
grid5=pv.UnstructuredGrid(tetraedros[4].ravel(),tetratype,pontos)
pl.add_mesh(grid5,color="pink",opacity=0.7,show_edges=True,edge_color="black",line_width=2)
cub=pv.UnstructuredGrid(cubo.ravel(),cubtype,pontos)
pl.add_mesh(cub,color="white",opacity=0.1,show_edges=True,edge_color="black")
pl.add_axes(
    xlabel="X",
    ylabel="Y",
    zlabel="Z",
    line_width=3,
    interactive=True
)
pl.subplot(1,2)
grid6=pv.UnstructuredGrid(tetraedros[5].ravel(),tetratype,pontos)
pl.add_mesh(grid6,color="purple",opacity=0.7,show_edges=True,edge_color="black",line_width=2)
cub=pv.UnstructuredGrid(cubo.ravel(),cubtype,pontos)
pl.add_mesh(cub,color="white",opacity=0.1,show_edges=True,edge_color="black")
pl.add_axes(
    xlabel="X",
    ylabel="Y",
    zlabel="Z",
    line_width=3,
    interactive=True
)


def alinhar_camaras(vista, negativa=False):
    """Alinha todas as câmaras com uma vista ortogonal 2D."""
    for renderer in pl.renderers:
        if vista == "yz":
            renderer.view_yz(negative=negativa)
        elif vista == "xz":
            renderer.view_xz(negative=negativa)
        renderer.enable_parallel_projection()
        renderer.reset_camera()
    pl.render()


pl.add_key_event("Left", lambda: alinhar_camaras("yz", negativa=True))
pl.add_key_event("Right", lambda: alinhar_camaras("yz"))
pl.add_key_event("Up", lambda: alinhar_camaras("xz"))
pl.add_key_event("Down", lambda: alinhar_camaras("xz", negativa=True))

for indice, (linha, coluna) in enumerate(((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)), start=1):
    pl.subplot(linha, coluna)
    pl.add_text(f"T{indice}", position="upper_left", color="black", font_size=18)


if modo_relatorio:
    pasta = Path(__file__).resolve().parents[1] / "output" / "Print"
    pasta.mkdir(parents=True, exist_ok=True)

    vistas = {
        "isometrica": lambda renderer: renderer.view_isometric(),
        "frontal_xy": lambda renderer: renderer.view_xy(),
        "lateral_yz": lambda renderer: renderer.view_yz(),
        "superior_xz": lambda renderer: renderer.view_xz(),
    }
    for nome, aplicar_vista in vistas.items():
        for renderer in pl.renderers:
            aplicar_vista(renderer)
            renderer.enable_parallel_projection()
            renderer.reset_camera()
        pl.render()
        pl.screenshot(str(pasta / f"divisao-cubo-6-tetraedros-{nome}.png"))
    pl.close()
else:
    pl.show()

