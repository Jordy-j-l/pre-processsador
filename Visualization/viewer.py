import numpy as np
import pyvista as pv
from pyvista import CellType


class Show:

    @staticmethod
    def cubes(plotter,cubes_elements,points_array,color="blue"):
        #arrays e afim
        cubes_type = np.array([CellType.HEXAHEDRON] * len(cubes_elements))


        #show Default
        pl=plotter
        grid = pv.UnstructuredGrid(cubes_elements,cubes_type,points_array)
        pl.add_mesh(grid,color=color,opacity=0.8,show_edges=True)
        return pl

    @staticmethod
    def tetrahedron(plotter,tetrahedron_elements,points_array,color="green",multi_color=False):
        tetra_type = np.array([CellType.TETRA] * len(tetrahedron_elements))

        if multi_color==False:
            pl=plotter
            grid = pv.UnstructuredGrid(tetrahedron_elements, tetra_type, points_array)
            pl.add_mesh(grid, color=color, opacity=0.8, show_edges=True)
            return pl


    @staticmethod
    def points(plotter,points_array,color="red"):
        # show Default
        pl=plotter
        grid = pv.PolyData(points_array)
        pl.add_mesh(grid, color=color, opacity=0.8, show_edges=True)
        return pl
