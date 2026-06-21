import numpy as np
import pyvista as pv
from pyvista import CellType

class Viewer:

    def __init__(self,pl,tetrahedron_elements,cubos_elements,points_array):
        self.tetrahedron_elements=tetrahedron_elements
        self.cubos_elements=cubos_elements
        self.points_array=points_array
        self.pl=pl#Ploter
        self.tetra_T1 = np.empty((4, 5), dtype=int)
        self.tetra_T2 = np.empty((4, 5), dtype=int)
        self.tetra_T3 = np.empty((4, 5), dtype=int)
        self.tetra_T4 = np.empty((4, 5), dtype=int)
        self.tetra_T5 = np.empty((4, 5), dtype=int)
        self.initTetra()
        print("T1\n",self.tetra_T1,"T2\n",self.tetra_T2,"T3\n",self.tetra_T3,"T4\n",self.tetra_T4,"T5\n",self.tetra_T5)

    def initTetra(self):

        count=0
        for i in range(0, len(self.tetrahedron_elements), 5):
            self.tetra_T1[count] = self.tetrahedron_elements[i]
            count+=1
        count=0
        for i in range(1, len(self.tetrahedron_elements), 5):
            self.tetra_T2[count] = self.tetrahedron_elements[i]
            count += 1
        count = 0
        for i in range(2, len(self.tetrahedron_elements), 5):
            self.tetra_T3[count] = self.tetrahedron_elements[i]
            count += 1
        count = 0
        for i in range(3, len(self.tetrahedron_elements), 5):
            self.tetra_T4[count] = self.tetrahedron_elements[i]
            count += 1
        count = 0
        for i in range(4, len(self.tetrahedron_elements), 5):
            self.tetra_T5[count] = self.tetrahedron_elements[i]
            count += 1


    def tetraType(self,type,color="green"):
        self.pl
        if type=="T1":
            tetra_type = np.array([CellType.TETRA] * len(self.tetra_T1))
            grid = pv.UnstructuredGrid(self.tetra_T1, tetra_type, self.points_array)
            self.pl.add_mesh(grid,name="T1", color=color, opacity=0.8, show_edges=True)
        if type=="T2":
            tetra_type = np.array([CellType.TETRA] * len(self.tetra_T2))
            grid = pv.UnstructuredGrid(self.tetra_T2, tetra_type, self.points_array)
            self.pl.add_mesh(grid,name="T2", color=color, opacity=0.8, show_edges=True)
        if type=="T3":
            tetra_type = np.array([CellType.TETRA] * len(self.tetra_T3))
            grid = pv.UnstructuredGrid(self.tetra_T3, tetra_type, self.points_array)
            self.pl.add_mesh(grid,name="T3", color=color, opacity=0.8, show_edges=True)
        if type=="T4":
            tetra_type = np.array([CellType.TETRA] * len(self.tetra_T4))
            grid = pv.UnstructuredGrid(self.tetra_T4, tetra_type, self.points_array)
            self.pl.add_mesh(grid,name="T4", color=color, opacity=0.8, show_edges=True)
        if type=="T5":
            tetra_type = np.array([CellType.TETRA] * len(self.tetra_T5))
            grid = pv.UnstructuredGrid(self.tetra_T5, tetra_type, self.points_array)
            self.pl.add_mesh(grid,name="T5", color=color, opacity=0.8, show_edges=True)
        if type =="ALL":
            tetra_type = np.array([CellType.TETRA] * len(self.tetrahedron_elements))
            grid = pv.UnstructuredGrid(self.tetrahedron_elements, tetra_type, self.points_array)
            self.pl.add_mesh(grid,name="ALL", color=color, opacity=0.8, show_edges=True)

    def RemoveTetraType(self, type):

        self.pl.remove_actor(type)



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
        pl = plotter
        if multi_color is False:
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





