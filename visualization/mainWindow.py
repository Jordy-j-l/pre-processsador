from PySide6.QtWidgets import QMainWindow, QStackedWidget

from visualization.menuPrincipal import MenuPrincipal
from visualization.pagePlacasParalelas import PagePlacasParalelas
from visualization.page1Vara import Page1Vara
from visualization.page2Varas import Page2Varas
from visualization.pageMalhaView import PageMalhaView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PRÉ-PROCESSADOR 3D")
        self.resize(1100, 650)
        self.setMinimumSize(900, 600)

        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)

        self.menu_principal = MenuPrincipal(
            abrir_placas=self.showPagePlacas,
            abrir_1_vara=self.showPage1Vara,
            abrir_2_varas=self.showPage2Varas,
            abrir_malha=self.showPageMalhaView
        )

        self.page_placas = PagePlacasParalelas(voltar=self.showMenuPrincipal)
        self.page_1_vara = Page1Vara()
        self.page_2_varas = Page2Varas()
        self.page_malha_view = PageMalhaView()

        self.pages.addWidget(self.menu_principal)
        self.pages.addWidget(self.page_placas)
        self.pages.addWidget(self.page_1_vara)
        self.pages.addWidget(self.page_2_varas)
        self.pages.addWidget(self.page_malha_view)

        self.showMenuPrincipal()

    def showMenuPrincipal(self):
        self.pages.setCurrentWidget(self.menu_principal)

    def showPagePlacas(self):
        self.pages.setCurrentWidget(self.page_placas)

    def showPage1Vara(self):
        self.pages.setCurrentWidget(self.page_1_vara)

    def showPage2Varas(self):
        self.pages.setCurrentWidget(self.page_2_varas)

    def showPageMalhaView(self):
        self.pages.setCurrentWidget(self.page_malha_view)

