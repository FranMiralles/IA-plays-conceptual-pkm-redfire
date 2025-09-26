import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QPixmap, QMovie, QFont
from PyQt5.QtCore import Qt
import requests
from io import BytesIO
from tempfile import NamedTemporaryFile

class MapViewer(QWidget):
    def __init__(self, individual):
        super().__init__()
        print(individual)
        # Descargar GIF y guardarlo temporalmente
        url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/1.gif"
        gif_data = requests.get(url).content
        tmp = NamedTemporaryFile(delete=False, suffix=".gif")
        tmp.write(gif_data)
        tmp.close()

        self.setWindowTitle("Mapa con labels relativos")
        self.setGeometry(200, 200, 1000, 750)

        # --- Imagen base ---
        self.map_label = QLabel(self)
        self.pixmap = QPixmap("images/map.png")
        self.map_label.setPixmap(self.pixmap)
        self.map_label.setScaledContents(True)

        # --- GIF 1 ---
        self.gif1 = QLabel(self)
        self.movie1 = QMovie(tmp.name)
        self.gif1.setMovie(self.movie1)
        self.pos1 = (0.25, 0.45)  # posición relativa
        self.movie1.start()

        # --- GIF 2 ---
        self.gif2 = QLabel(self)
        self.movie2 = QMovie(tmp.name)
        self.gif2.setMovie(self.movie2)
        self.pos2 = (0.6, 0.55)
        self.movie2.start()

        # --- Texto ---
        self.text_label = QLabel("Aquí empieza la aventura!", self)
        self.text_label.setStyleSheet("color: white; background-color: rgba(0,0,0,150); padding: 4px;")
        self.pos_text = (0.4, 0.15)

        # Forzar el ajuste inicial
        self.resizeEvent(None)

    def resizeEvent(self, event):
        w = self.width()
        h = self.height()

        # Redimensionar el mapa
        self.map_label.resize(w, h)

        # Calcular tamaño relativo para los GIFs (ejemplo: 10% del ancho de la ventana)
        reductor_gif = 0.8
        gif_size = int(w * 0.075 * reductor_gif), int(h * 0.1 * reductor_gif)

        # --- GIF 1 ---
        self.gif1.move(int(w * self.pos1[0]), int(h * self.pos1[1]))
        self.gif1.resize(*gif_size)
        self.movie1.setScaledSize(self.gif1.size())

        # --- GIF 2 ---
        self.gif2.move(int(w * self.pos2[0]), int(h * self.pos2[1]))
        self.gif2.resize(*gif_size)
        self.movie2.setScaledSize(self.gif2.size())

        # --- Texto ---
        self.text_label.move(int(w * self.pos_text[0]), int(h * self.pos_text[1]))
        font_size = max(int(h * 0.03), 8)  # fuente proporcional a la altura
        self.text_label.setFont(QFont("Arial", font_size))
        self.text_label.adjustSize()

if __name__ == "__main__":
    individual=[
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
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
    window = MapViewer(individual)
    window.show()
    sys.exit(app.exec_())