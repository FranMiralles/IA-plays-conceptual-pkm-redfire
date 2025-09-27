import base64
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap, QMovie, QFont
from PyQt5.QtCore import Qt
import requests
from io import BytesIO
from tempfile import NamedTemporaryFile
from battle_simulator import dataset
from individual import INDIVIDUAL

PK_POSITIONS=[
    (0.205, 0.712), # PUEBLO PALETA
    (0.205, 0.625), # RUTA 1
    (0.1225, 0.545), # RUTA 22
    (0.205, 0.485), # RUTA 2
    (0.205, 0.405), # BOSQUE VERDE
    (0.285, 0.323), # RUTA 3
    (0.51, 0.266), # RUTA 4
    (0.41, 0.266), # MONTE MOON
    (0.62, 0.208), # RUTA 24
    (0.68, 0.155), # RUTA 25
    (0.62, 3495), # RUTA 5
    (0.62, 0.518), # RUTA 6
    (0.726, 0.6), # RUTA 11
    (0.668, 0.6), # CUEVA DIGLETT
    (0.7, 0.266), # RUTA 9
    (0.786, 0.376), # RUTA 10
    (0.786, 0.266), # TUNEL ROCA
    (0.7, 0.435), # RUTA 8
    (0.555, 0.435), # RUTA 7
    (0.41, 0.435), # RUTA 16
    (0.786, 0.435), # TORRE POKEMON
    (0.786, 0.6), # RUTA 12
    (0.726, 0.712), # RUTA 13
    (0.668, 0.712), # RUTA 14
    (0.62, 0.768), # RUTA 15
    (0.54, 0.768), # ZONA SAFARI
    (0.41, 0.768), # RUTA 18
    (0.33, 0.6), # RUTA 17
    (0.54, 0.88), # RUTA 19
    (0.45, 0.88), # RUTA 20
    (0.205, 0.8), # RUTA 21
    (0.36, 0.88), # ISLAS ESPUMA
    (0.205, 0.88), # MANSION PKM
    (0.786, 0.323), # CENTRAL ENERGIA
    (0.1225, 0.435), # RUTA 23
    (0.1225, 0.323), # CALLE VICTORIA
]

class MapPanel(QWidget):
    def __init__(self, pkGIFList: list):
        super().__init__()

        self.setMouseTracking(True)

        # --- Imagen base ---
        self.map_label = QLabel(self)
        self.pixmap = QPixmap("images/map.png")
        self.map_label.setPixmap(self.pixmap)
        self.map_label.setScaledContents(True)

        # Widgets que representan cada ruta (gif o texto)
        self.route_widgets = []
        for pkGIF in pkGIFList:
            gif_label = QLabel(self)
            movie = QMovie(pkGIF)
            gif_label.setMovie(movie)
            movie.start()
            self.route_widgets.append((gif_label, movie))

        # --- Texto ---
        self.text_label = QLabel("Individuo: Factible", self)
        self.text_label.setStyleSheet("color: white; background-color: rgba(0,0,0,150); padding: 4px;")
        self.pos_text = (0, 0)

    def resizeEvent(self, event):
        w = self.width()
        h = self.height()

        # Redimensionar el mapa
        self.map_label.resize(w, h)

        # Calcular tamaño relativo para los GIFs / labels
        reductor_gif = 0.7
        widget_size = int(w * 0.075 * reductor_gif), int(h * 0.1 * reductor_gif)

        for i, (widget, movie) in enumerate(self.route_widgets):
            x = int(w * PK_POSITIONS[i][0])
            y = int(h * PK_POSITIONS[i][1])

            widget.move(x, y)
            widget.resize(*widget_size)
            movie.setScaledSize(widget.size())

        # --- Texto general ---
        self.text_label.move(int(w * self.pos_text[0]), int(h * self.pos_text[1]))
        font_size = max(int(h * 0.03), 8)  # fuente proporcional a la altura
        self.text_label.setFont(QFont("Arial", font_size))
        self.text_label.adjustSize()

class App(QWidget):
    def __init__(self, individual):
        super().__init__()

        pkGIFList = []
        for pkmID in individual[0]:
            if pkmID is None:
                pkGIFList.append("./pkm_data/sprites/pokeball_loading.gif")
            else:
                gif_path = dataset["pkdex"][str(pkmID)]["sprite"]["front"]
                pkGIFList.append(gif_path)

        self.setWindowTitle("Fenotipo")
        self.setGeometry(200, 200, 1000, 750)

        # --- Layout principal (horizontal) ---
        layout = QHBoxLayout(self)

        # --- Menú lateral ---
        menu = QVBoxLayout()
        menu.setAlignment(Qt.AlignTop)

        btn1 = QPushButton("Opción 1")
        btn2 = QPushButton("Opción 2")
        btn3 = QPushButton("Opción 3")

        menu.addWidget(btn1)
        menu.addWidget(btn2)
        menu.addWidget(btn3)

        # Contenedor del menú
        menu_widget = QWidget()
        menu_widget.setLayout(menu)
        menu_widget.setFixedWidth(300)  # ancho fijo del menú

        # --- Panel del mapa ---
        self.map_panel = MapPanel(pkGIFList)

        # Añadir al layout principal
        layout.addWidget(menu_widget)
        layout.addWidget(self.map_panel, stretch=1)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App(INDIVIDUAL)
    window.show()
    sys.exit(app.exec_())