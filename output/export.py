import numpy as np


class Export:
    def __init__(self,element_list,point_list,vector_list,rho=1,v=100):
        self.element_list = element_list
        self.point_list = point_list
        self.vector_list = vector_list
        self.rho=rho
        self.v=v
        self.expor_tp = np.empty((len(self.point_list), 4))
        self.export_tetra = np.empty((len(self.element_list), 5))





    def exportPointList(self,name="pontos.txt"):
        for i in range(len(self.point_list)):
            self.expor_tp[i][0] = self.point_list[i][0]
            self.expor_tp[i][1] = self.point_list[i][1]
            self.expor_tp[i][2] = self.point_list[i][2]
            self.expor_tp[i][3] = -1 if i < self.vector_list[0] else self.v if i < self.vector_list[1] + self.vector_list[0] else 0
        np.savetxt(f"output/downloads/{name}", self.expor_tp, fmt="%.6f")

    def exportElementList(self,name="elementos.txt"):
        for i in range(len(self.element_list)):
            self.export_tetra[i, 0] = self.element_list[i][1]
            self.export_tetra[i, 1] = self.element_list[i][2]
            self.export_tetra[i, 2] = self.element_list[i][3]
            self.export_tetra[i, 3] = self.element_list[i][4]
            self.export_tetra[i, 4] = self.rho
        np.savetxt(f"output/downloads/{name}", self.export_tetra, fmt="%.6f")
    def exportVector(self,name="Vetor.txt"):
        np.savetxt(f"output/downloads/{name}",  self.vector_list, fmt="%d")

    def exportAll(self,name_p="pontos.txt",name_e="elementos.txt",name_v="Vetor.txt"):
        self.exportPointList(name_p)
        self.exportElementList(name_e)
        self.exportVector(name_v)

