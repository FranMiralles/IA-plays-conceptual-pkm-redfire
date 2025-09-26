import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap, QMovie, QFont
from PyQt5.QtCore import Qt
import requests
from io import BytesIO
from tempfile import NamedTemporaryFile
from battle_simulator import dataset

PK_POSITIONS=[
    (0.205, 0.715), # PUEBLO PALETA
    (0.205, 0.625), # RUTA 1
    (0.14, 0.548), # RUTA 22
    (0.205, 0.485), # RUTA 2
    (0.205, 0.41), # BOSQUE VERDE
    (0.28, 0.325), # RUTA 3
    (0.51, 0.27), # RUTA 4
    (0.41, 0.27), # MONTE MOON
    (0.62, 0.205), # RUTA 24
    (0.68, 0.16), # RUTA 25
    (0.62, 0.35), # RUTA 5
    (0.62, 0.53), # RUTA 6
    (0.73, 0.61), # RUTA 11
    (0.68, 0.61), # CUEVA DIGLETT
    (0.7, 0.27), # RUTA 9
    (0.8, 0.38), # RUTA 10
    (0.8, 0.32), # TUNEL ROCA
    (0.70, 0.45), # RUTA 8
    (0.56, 0.45), # RUTA 7
    (0.40, 0.45), # RUTA 16
    (0.8, 0.45), # TORRE POKEMON
    (0.8, 0.61), # RUTA 12
    (0.73, 0.72), # RUTA 13
    (0.67, 0.75), # RUTA 14
    (0.60, 0.78), # RUTA 15
    (0.54, 0.78), # ZONA SAFARI
    (0.41, 0.78), # RUTA 18
    (0.33, 0.55), # RUTA 17
    (0.54, 0.85), # RUTA 19
    (0.47, 0.89), # RUTA 20
    (0.47, 0.89), # RUTA 21
    (0.34, 0.89), # ISLAS ESPUMA
    (0.2, 0.89), # MANSION PKM
    (0.8, 0.27), # CENTRAL ENERGIA
    (0.12, 0.45), # RUTA 23
    (0.12, 0.325), # CALLE VICTORIA
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

        # GIFs
        self.gif_widgets = []
        for pkGIF in pkGIFList:
            gif_label = QLabel(self)
            movie = QMovie(pkGIF)
            gif_label.setMovie(movie)
            movie.start()
            self.gif_widgets.append((gif_label, movie))

        # --- Texto ---
        self.text_label = QLabel("Aquí empieza la aventura!", self)
        self.text_label.setStyleSheet("color: white; background-color: rgba(0,0,0,150); padding: 4px;")
        self.pos_text = (0, 0)

    def resizeEvent(self, event):
        w = self.width()
        h = self.height()

        # Redimensionar el mapa
        self.map_label.resize(w, h)

        # Calcular tamaño relativo para los GIFs
        reductor_gif = 0.7
        gif_size = int(w * 0.075 * reductor_gif), int(h * 0.1 * reductor_gif)

        for i in range(len(self.gif_widgets)):
            gif_label, movie = self.gif_widgets[i]
            x = int(w * PK_POSITIONS[i][0])
            y = int(h * PK_POSITIONS[i][1])

            gif_label.move(x, y)
            gif_label.resize(*gif_size)
            movie.setScaledSize(gif_label.size())

        # --- Texto ---
        self.text_label.move(int(w * self.pos_text[0]), int(h * self.pos_text[1]))
        font_size = max(int(h * 0.03), 8)  # fuente proporcional a la altura
        self.text_label.setFont(QFont("Arial", font_size))
        self.text_label.adjustSize()

    
    def mouseMoveEvent(self, event):
        w, h = self.width(), self.height()
        x, y = event.x(), event.y()

        # Coordenadas relativas (0.0 - 1.0)
        rel_x, rel_y = x / w, y / h

        # Mostrar en el label de coordenadas
        
        print(f"Mouse: ({x}, {y}) | Rel: ({rel_x:.2f}, {rel_y:.2f})")
        


class App(QWidget):
    def __init__(self, individual):
        super().__init__()
        print(individual)

        pkGIFList = []
        for pkmID in individual[0]:
            url = dataset["pkdex"][str(pkmID)]["sprite"]["front"]
            gif_data = requests.get(url).content
            tmp = NamedTemporaryFile(delete=False, suffix=".gif")
            tmp.write(gif_data)
            tmp.close()
            pkGIFList.append(tmp.name)
        # Descargar GIF y guardarlo temporalmente
        url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/1.gif"
        gif_data = requests.get(url).content
        tmp = NamedTemporaryFile(delete=False, suffix=".gif")
        tmp.write(gif_data)
        tmp.close()

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
        menu_widget.setFixedWidth(200)  # ancho fijo del menú

        # --- Panel del mapa ---
        self.map_panel = MapPanel(pkGIFList)

        # Añadir al layout principal
        layout.addWidget(menu_widget)
        layout.addWidget(self.map_panel, stretch=1)

        self.setLayout(layout)


if __name__ == "__main__":
    individual=[
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [
            [1, 2, 3, 1, 2],
            [1, 2, 3, 2, 2, 6],
            [1, 2, 3, 2, 3, 6],
            [1, 2, 3, 3, 3, 6],
            [1, 2, 3, 2, 3, 6],
            [1, 2, 3, 2, 3, 6],
            [1, 2, 3, 2, 3, 6],
            [1, 2, 3, 2, 3, 6],
            [1, 2, 3, 2, 3, 6],
            [1, 2, 3, 2, 3, 6],
            [1, 2, 3, 2, 3, 6],
            [1, 2, 3, 2, 3, 6],
            [1, 2, 3, 2, 3, 6],
            [1, 2, 3, 2, 3, 29],
        ]
    ]
    app = QApplication(sys.argv)
    window = App(individual)
    window.show()
    sys.exit(app.exec_())