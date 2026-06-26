"""
===================================================================================================================
                                                PRE-PROCESSING FEM
 Esse é o meu projeto final do curso de engenharia informatica um pre-processador de elementos finitos tetraedicos
===================================================================================================================
                                                        NOMENCLATURA
                                    camelCase               -          Funções
                                    PascalCase              -          Classes
                                    snake_case              -          Variaveis
                                    UPPER_SNAKE_CASE        -          Constantes
                                    kebab-case              -          Ficheiros
=====================================================================================================================
                                                    Conventional Commits:
                                | Tipo       | Uso                                   |
                                | ---------- | ------------------------------------- |
                                | `feat`     | nova funcionalidade                   |
                                | `fix`      | correção de erro                      |
                                | `refactor` | reorganização sem mudar comportamento |
                                | `docs`     | documentação                          |
                                | `test`     | testes                                |
                                | `style`    | formatação                            |
                                | `chore`    | tarefas gerais                        |
                                | `perf`     | melhoria de desempenho                |

"""




import sys
from PySide6.QtWidgets import QApplication
from visualization.mainWindow import MainWindow

def menuPrincipal():
    pass
    #Menu principal do software
    """
            PRÉ-PROCESSADOR 3D
                BUILDER
        -> Placas Paralelas
        -> 1 Vara
        -> 2 Vara
              Visualização 
        -> Malha
    """

def VisualizaçãoCall():
    pass
    #Lista de Funções
    """
    View 2d
    View 3d
    View ALL tetraedros ON/OFF
    View Tetraedro 1
    View Tetraedro 2
    View Tetraedro 3
    View Tetraedro 4
    View Tetraedro 5
    View Points ON/OFF
    View Cubes
    View edges ON/OFF
    Opacity
    COR dos elementos(definir cada uma delas)
    
    """




def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()