import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget
from PyQt5.QtGui import QPixmap, QMovie, QFont, QPainter, QColor, QPainterPath
from PyQt5.QtCore import Qt, QRectF
from battle_simulator import *
from route_data.trainers import PREVIOUS_ROUTES_TO_TRAINER
from genetic_operators import *
import re

STYLE_SHEET = """
            /* Estilos modernos */
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
            
            /* Menú principal */
            QWidget[objectName="main_menu"] {
                background-color: #2c3e50;
                border-right: 1px solid #34495e;
            }
            
            /* Submenús */
            QWidget[objectName="submenu_map"] {
                background-color: #34495e;
                border-right: 1px solid #2c3e50;
            }
            
            QWidget[objectName="submenu_combat"] {
                background-color: #34495e;
                border-right: 1px solid #2c3e50;
            }
            
            /* Botones principales */
            QPushButton#main_btn {
                background-color: #34495e;
                color: #ecf0f1;
                border: none;
                border-radius: 10px;
                padding: 6px 12px;
                font-weight: bold;
                text-align: right;
                margin: 0px;
            }
            
            QPushButton#main_btn:hover {
                background-color: #3c5a78;
            }
            
            QPushButton#main_btn[selected="true"] {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                border-left: 4px solid #c0392b;
            }
            
            /* Botones de submenú */
            QPushButton#sub_btn {
                background-color: #2c3e50;
                color: #bdc3c7;
                border: none;
                border-radius: 10px;
                padding: 6px 12px;
                text-align: left;
                margin: 1px;
            }
            
            QPushButton#sub_btn:hover {
                background-color: #3c5a78;
                color: #ecf0f1;
            }
            
            QPushButton#sub_btn[selected="true"] {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                border-left: 4px solid #c0392b;
            }
            
            /* Efectos generales para botones */
            QPushButton:pressed {
                background-color: #16a085;
            }
        """

    # Estilo de los botones
button_style = """
    QPushButton {
        background-color: rgba(70, 70, 70, 1);
        color: white;
        font-weight: bold;
        border: 2px solid white;
        border-radius: 10px;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: rgba(100, 100, 100, 1);
    }
    QPushButton:pressed {
        background-color: rgba(50, 50, 50, 1);
    }
"""

PK_POSITIONS=[
    (0.181, 0.629), # PUEBLO PALETA
    (0.181, 0.535), # RUTA 1
    (0.099, 0.455), # RUTA 22
    (0.181, 0.4), # RUTA 2
    (0.181, 0.32), # BOSQUE VERDE
    (0.262, 0.237), # RUTA 3
    (0.487, 0.18), # RUTA 4
    (0.387, 0.18), # MONTE MOON
    (0.597, 0.118), # RUTA 24
    (0.677, 0.07), # RUTA 25
    (0.597, 0.2595), # RUTA 5
    (0.597, 0.428), # RUTA 6
    (0.703, 0.515), # RUTA 11
    (0.639, 0.515), # CUEVA DIGLETT
    (0.677, 0.18), # RUTA 9
    (0.764, 0.286), # RUTA 10
    (0.764, 0.18), # TUNEL ROCA
    (0.677, 0.35), # RUTA 8
    (0.532, 0.35), # RUTA 7
    (0.387, 0.35), # RUTA 16
    (0.764, 0.35), # TORRE POKEMON
    (0.764, 0.515), # RUTA 12
    (0.703, 0.628), # RUTA 13
    (0.639, 0.628), # RUTA 14
    (0.597, 0.685), # RUTA 15
    (0.514, 0.685), # ZONA SAFARI
    (0.387, 0.685), # RUTA 18
    (0.307, 0.515), # RUTA 17
    (0.514, 0.795), # RUTA 19
    (0.427, 0.795), # RUTA 20
    (0.181, 0.705), # RUTA 21
    (0.337, 0.795), # ISLAS ESPUMA
    (0.181, 0.795), # MANSION PKM
    (0.764, 0.233), # CENTRAL ENERGIA
    (0.099, 0.35), # RUTA 23
    (0.099, 0.237), # CALLE VICTORIA
]

ROUTE_NAMES = [
    "PUEBLO PALETA", "RUTA 1", "RUTA 22", "RUTA 2", "BOSQUE VERDE",
    "RUTA 3", "RUTA 4", "MONTE MOON", "RUTA 24", "RUTA 25",
    "RUTA 5", "RUTA 6", "RUTA 11", "CUEVA DIGLETT", "RUTA 9",
    "RUTA 10", "TÚNEL ROCA", "RUTA 8", "RUTA 7", "RUTA 16",
    "TORRE POKÉMON", "RUTA 12", "RUTA 13", "RUTA 14", "RUTA 15",
    "ZONA SAFARI", "RUTA 18", "RUTA 17", "RUTA 19", "RUTA 20",
    "RUTA 21", "ISLAS ESPUMA", "MANSIÓN POKÉMON", "CENTRAL ENERGÍA",
    "RUTA 23", "CALLE VICTORIA"
]

# Label con dos colores separados verticalmente
class DualColorLabel(QLabel):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # bordes suaves

        # Crear una ruta con bordes redondeados
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 10, 10)
        painter.setClipPath(path)  # recorta el área al radio

        # Mitad superior - Color 1
        painter.fillRect(0, 0, self.width(), self.height() // 2, QColor(0, 0, 255, 65))

        # Mitad inferior - Color 2
        painter.fillRect(0, self.height() // 2, self.width(), self.height() // 2, QColor(255, 0, 0, 65))

        # Dibuja el texto del QLabel normalmente
        super().paintEvent(event)
        
SEPARATOR = " : "
def prepare_entire_logs(entire_logs):
    def get_pkmID(name: str):
        for key in dict(dataset["pkdex"]).keys():
            if dataset["pkdex"][key]["name"] == name:
                return key
        return 0

    new_logs = []
    for log in entire_logs:
        new_log = []
        active_player_pkm = None
        active_rival_pkm = None
        for i in range(len(log)):
            if log[i].startswith("TURNO"):
                player_line = log[i + 1].split(" ")
                rival_line = log[i + 2].split(" ")
                active_player_pkm = get_pkmID(player_line[1]) + "," + player_line[3]
                active_rival_pkm = get_pkmID(rival_line[1]) + "," + rival_line[3]
                new_log.append(log[i] + SEPARATOR + active_player_pkm + SEPARATOR + active_rival_pkm)
                i += 2
            elif log[i].startswith("PLAYER") and "HP" not in str(log[i]):
                patron = r"\(.*\)"
                search = re.search(patron, log[i])
                if search:
                    damage = search.group(0)
                    damage = float(damage.split(", ")[1][:-1]) * 100
                    # Tengo que reescribir el pkm rival, por lo que busco el siguiente PLAYER con HP
                    for j in range(i, len(log)):
                        if log[j].startswith("RIVAL") and "HP" in str(log[j]):
                            rival_line = log[j].split(" ")
                            active_rival_pkm = get_pkmID(rival_line[1]) + "," + rival_line[3]
                            break
                    new_log.append(log[i] + SEPARATOR + active_player_pkm + SEPARATOR + active_rival_pkm)
                else:
                    # No daña
                    new_log.append(log[i] + SEPARATOR + active_player_pkm + SEPARATOR + active_rival_pkm)
            elif log[i].startswith("RIVAL") and "HP" not in str(log[i]):
                patron = r"\(.*\)"
                search = re.search(patron, log[i])
                if search:
                    damage = search.group(0)
                    damage = float(damage.split(", ")[1][:-1]) * 100
                    # Tengo que reescribir el pkm del jugador, por lo que busco el siguiente PLAYER con HP
                    for j in range(i, len(log)):
                        if log[j].startswith("PLAYER") and "HP" in str(log[j]):
                            player_line = log[j].split(" ")
                            active_player_pkm = get_pkmID(player_line[1]) + "," + player_line[3]
                            break
                    new_log.append(log[i] + SEPARATOR + active_player_pkm + SEPARATOR + active_rival_pkm)
                else:
                    # No daña
                    new_log.append(log[i] + SEPARATOR + active_player_pkm + SEPARATOR + active_rival_pkm)
            elif "recovers" in log[i]:
                new_log.append(log[i] + SEPARATOR + active_player_pkm + SEPARATOR + active_rival_pkm)
                

        new_logs.append(new_log)
    return new_logs

def select_direction(route_name: str):
    if route_name in ["PUEBLO PALETA", "RUTA 1", "RUTA 21", "MANSIÓN POKÉMON", "RUTA 5", "RUTA 6", "RUTA 22", "RUTA 23", "CALLE VICTORIA"]:
        return "left"
    if route_name in ["TÚNEL ROCA", "CENTRAL ENERGÍA", "RUTA 10", "TORRE POKÉMON", "RUTA 12", "RUTA 2", "BOSQUE VERDE"]:
        return "right"
    if route_name in ["ISLAS ESPUMA", "RUTA 20", "RUTA 19", "RUTA 17", "RUTA 16", "RUTA 7", "CUEVA DIGLETT", "RUTA 11", "RUTA 8", "RUTA 14", "RUTA 9", "RUTA 13"]:
        return "down"
    if route_name in ["RUTA 18", "RUTA 24", "RUTA 18", "RUTA 25", "TÚNEL ROCA", "RUTA 4", "RUTA 3", "MONTE MOON", "RUTA 15", "ZONA SAFARI"]:
        return "up"

class MapPanel(QWidget):
    def __init__(self, pkGIFList: list):
        super().__init__()
        self.setMinimumWidth(50)
        self.setMinimumHeight(50)
        self.setMouseTracking(True)
        # --- Imagen base ---
        self.map_label = QLabel(self)
        self.pixmap = QPixmap("images/map.png")
        self.map_label.setPixmap(self.pixmap)
        self.map_label.setScaledContents(True)

        # Widgets que representan cada ruta (gif o texto)
        self.route_widgets = []
        for i, pkGIF in enumerate(pkGIFList):
            gif_label = QLabel(self)
            movie = QMovie(pkGIF)
            gif_label.setMovie(movie)
            movie.start()

            name_label = QLabel(ROUTE_NAMES[i], self)
            name_label.setStyleSheet("color: white; background-color: rgba(0,0,0,150); padding: 2px;")
            name_label.adjustSize()
            
            name_label_direction = select_direction(ROUTE_NAMES[i])

            if pkGIF in ["./pkm_data/manual_sprites/not_captured.gif",
                        "./pkm_data/manual_sprites/not_captured_yet.gif"]:
                self.route_widgets.append((gif_label, movie, "ball", name_label, name_label_direction))
            else:
                self.route_widgets.append((gif_label, movie, "pkm", name_label, name_label_direction))


    def resizeEvent(self, event):
        w = self.width()
        h = self.height()

        # Redimensionar el mapa
        self.map_label.resize(w, h)

        # Calcular tamaño relativo para los GIFs / labels
        increment_gif = 1
        #widget_size_ball = int(w * 0.1 * reducer_gif), int(h * 0.15 * reducer_gif)
        widget_size_pkm = int(w * 0.1 * increment_gif), int(h * 0.15 * increment_gif)

        for i, (widget, movie, type, name_label, name_label_direction) in enumerate(self.route_widgets):
            if type == "pkm":
                x = int(w * PK_POSITIONS[i][0])
                y = int(h * PK_POSITIONS[i][1])
                if name_label_direction == "left":
                    name_label.move(int(x - name_label.width() + w * 0.02), int(y - name_label.height() + h * 0.15))
                if name_label_direction == "right":
                    name_label.move(int(x + w * 0.078), int(y - name_label.height() + h * 0.15))
                if name_label_direction == "down":
                    name_label.move(int(x + w * 0.025), int(y - name_label.height() + h * 0.18))
                if name_label_direction == "up":
                    name_label.move(int(x + w * 0.025), int(y - name_label.height() + h * 0.08))
            else:
                x = int(w * PK_POSITIONS[i][0])
                y = int(h * (PK_POSITIONS[i][1] + 0.05))
                if name_label_direction == "left":
                    name_label.move(int(x - name_label.width() + w * 0.02), int(y - name_label.height() + h * 0.1))
                if name_label_direction == "right":
                    name_label.move(int(x + w * 0.078), int(y - name_label.height() + h * 0.1))
                if name_label_direction == "down":
                    name_label.move(int(x + w * 0.025), int(y - name_label.height() + h * 0.13))
                if name_label_direction == "up":
                    name_label.move(int(x + w * 0.025), int(y - name_label.height() + h * 0.03))
            
            widget.resize(*widget_size_pkm)
            widget.move(x, y)
            movie.setScaledSize(widget.size())

            # Label a la izquierda del GIF
            #name_label.move(x - name_label.width(), y + widget.height()//2 - name_label.height()//2)
            
            font_size = max(int(h * 0.02), 1)
            name_label.setFont(QFont("Arial", font_size))
            name_label.adjustSize()


    def update_MapPanel(self, pkGIFList: list):
        """Actualiza la lista de sprites mostrados en el mapa"""
        # Eliminar los widgets anteriores
        for widget, movie, type, name_label, name_label_direction in self.route_widgets:
            widget.setParent(None)
            movie.stop()
            name_label.setParent(None)

        self.route_widgets = []

        # Crear los nuevos
        for i, pkGIF in enumerate(pkGIFList):
            gif_label = QLabel(self)
            movie = QMovie(pkGIF)
            gif_label.setMovie(movie)
            movie.start()
            gif_label.show()

            name_label = QLabel(ROUTE_NAMES[i], self)
            name_label.setStyleSheet("color: white; background-color: rgba(0,0,0,150); padding: 2px;")
            name_label.adjustSize()
            name_label.show()

            name_label_direction = select_direction(ROUTE_NAMES[i])

            if pkGIF in ["./pkm_data/manual_sprites/not_captured.gif",
                        "./pkm_data/manual_sprites/not_captured_yet.gif"]:
                self.route_widgets.append((gif_label, movie, "ball", name_label, name_label_direction))
            else:
                self.route_widgets.append((gif_label, movie, "pkm", name_label, name_label_direction))

        # Forzar redibujo y reposicionamiento
        self.update()
        self.resizeEvent(None)

class CombatPanel(QWidget):
    def __init__(self, teamsPreviewGIFList: list, entire_logs, starterID):
        super().__init__()
        self.setMinimumWidth(50)
        self.setMinimumHeight(50)
        self.setMouseTracking(True)
        # --- Imagen base ---
        self.map_label = QLabel(self)
        self.pixmap = QPixmap("images/forest.png")
        self.map_label.setPixmap(self.pixmap)
        self.map_label.setScaledContents(True)
        
        # Lista de equipos del jugador (cada equipo es una lista de GIFs)
        self.teamsPreviewGIFList = teamsPreviewGIFList
        self.current_team_index = 0
        # Definir equipos rivales (pkmID)
        self.rival_teams = {
            "RIVAL_RUTA_22": [16, 4] if starterID == 1 else [16, 7] if starterID == 4 else [16, 1],
            "GYM_PLATEADA": [74, 95],
            "RIVAL_CELESTE": [17, 19, 4] if starterID == 1 else [17, 19, 7] if starterID == 4 else [17, 19, 1],
            "GYM_CELESTE": [120, 121],
            "RIVAL_CARMIN": [17, 20, 64, 5] if starterID == 1 else [17, 20, 64, 8] if starterID == 4 else [17, 20, 64, 2],
            "GYM_CARMIN": [100, 25, 26],
            "RIVAL_TORRE_PKM": [17, 102, 130, 64, 5] if starterID == 1 else [17, 58, 102, 64, 8] if starterID == 4 else [17, 130, 58, 64, 2],
            "GYM_AZULONA": [71, 114, 45],
            "GIOVANNI_AZULONA": [95, 111, 115],
            "RIVAL_AZAFRAN": [18, 102, 130, 65, 6] if starterID == 1 else [18, 58, 102, 65, 9] if starterID == 4 else [18, 130, 58, 65, 3],
            "GIOVANNI_AZAFRAN": [33, 111, 115, 31],
            "GYM_FUCSIA": [109, 109, 89, 110],
            "GYM_AZAFRAN": [64, 49, 122, 65],
            "GYM_CANELA": [58, 77, 78, 59],
            "GYM_VERDE": [111, 51, 34, 31, 111],
            "RIVAL_VERDE": [18, 111, 102, 130, 65, 6] if starterID == 1 else [18, 111, 58, 102, 65, 9] if starterID == 4 else [18, 111, 130, 58, 65, 3],
            "ALTO_MANDO_LORELEI": [87, 91, 80, 124, 131],
            "ALTO_MANDO_BRUNO": [95, 107, 106, 95, 68],
            "ALTO_MANDO_AGATHA": [94, 42, 93, 24, 94],
            "ALTO_MANDO_LANCE": [130, 148, 148, 142, 149],
            "RIVAL_CAMPEON": [18, 112, 65, 103, 130, 6] if starterID == 1 else [18, 112, 65, 59, 103, 9] if starterID == 4 else [18, 112, 65, 130, 59, 3]
        }
        
        # Convertir IDs rivales a GIFs
        self.rival_teams_gifs = {}
        for trainer, team_ids in self.rival_teams.items():
            gif_team = []
            for pkm_id in team_ids:
                gif_path = str(dataset["pkdex"][str(pkm_id)]["sprite"]["front"]).replace("normalized_sprites", "sprites")
                gif_team.append(gif_path)
            self.rival_teams_gifs[trainer] = gif_team
        
        # Mapeo de nombres de botones a claves de equipos rivales
        self.button_to_rival_key = {
            "RIVAL RUTA 22": "RIVAL_RUTA_22",
            "GYM PLATEADA": "GYM_PLATEADA",
            "RIVAL CELESTE": "RIVAL_CELESTE",
            "GYM CELESTE": "GYM_CELESTE", 
            "RIVAL CARMIN": "RIVAL_CARMIN",
            "GYM CARMIN": "GYM_CARMIN",
            "RIVAL TORRE PKM": "RIVAL_TORRE_PKM",
            "GYM AZULONA": "GYM_AZULONA",
            "GIOVANNI AZULONA": "GIOVANNI_AZULONA",
            "RIVAL AZAFRAN": "RIVAL_AZAFRAN",
            "GIOVANNI AZAFRAN": "GIOVANNI_AZAFRAN",
            "GYM FUCSIA": "GYM_FUCSIA",
            "GYM AZAFRAN": "GYM_AZAFRAN",
            "GYM CANELA": "GYM_CANELA",
            "GYM VERDE": "GYM_VERDE",
            "RIVAL VERDE": "RIVAL_VERDE",
            "ALTO MANDO LORELEI": "ALTO_MANDO_LORELEI",
            "ALTO MANDO BRUNO": "ALTO_MANDO_BRUNO",
            "ALTO MANDO AGATHA": "ALTO_MANDO_AGATHA",
            "ALTO MANDO LANCE": "ALTO_MANDO_LANCE",
            "RIVAL CAMPEON": "RIVAL_CAMPEON"
        }
        
        # Listas para almacenar los widgets de Pokémon
        self.player_widgets = []
        self.rival_widgets = []


        # LOGS
        # Almacenar los logs completos
        self.entire_logs = entire_logs

        self.labelLog = QLabel("", self)  # Hacerlo atributo de la clase
        self.labelLog.setFont(QFont("Arial", 12))
        self.labelLog.setStyleSheet("color: white; font-weight: bold; background-color: rgba(0, 0, 0, 0.7); padding: 5px; border-radius: 10px;")
        self.labelLog.setAlignment(Qt.AlignLeft)

        # Label del team preview
        self.teamPreview =  DualColorLabel("", self)
        self.teamPreviewText = QLabel("TEAM PREVIEW", self)  # Hacerlo atributo de la clase
        self.teamPreviewText.setStyleSheet("color: white; font-weight: bold; background-color: rgba(0, 0, 0, 0.6); padding: 5px; border-top-left-radius: 10px; border-top-right-radius: 10px;")
        self.teamPreviewText.setAlignment(Qt.AlignCenter)

        # BOTONES
        self.btnNextTurn = QPushButton("NEXT TURN", self)
        self.btnPastTurn = QPushButton("PAST TURN", self)
        self.btnStartBattle = QPushButton("FIRST TURN", self)
        self.btnEndBattle = QPushButton("LAST TURN", self)
        
        # Conectar botones a sus funciones
        self.btnNextTurn.clicked.connect(self.next_turn)
        self.btnPastTurn.clicked.connect(self.past_turn)
        self.btnStartBattle.clicked.connect(self.start_battle)
        self.btnEndBattle.clicked.connect(self.end_battle)
        
        self.btnNextTurn.setStyleSheet(button_style)
        self.btnPastTurn.setStyleSheet(button_style)
        self.btnStartBattle.setStyleSheet(button_style)
        self.btnEndBattle.setStyleSheet(button_style)


        # Pkm activos
        self.team_active_pkmID = 1
        self.rival_active_pkmID = 1
        self.team_active_pkmLabel = QLabel(self)
        self.rival_active_pkmLabel = QLabel(self)
        self.team_active_pkmHP = QLabel("100% HP", self)
        self.team_active_pkmHP.setStyleSheet("""
            color: #FFD700;  /* Dorado */
            font-weight: bold;
            font-size: 12px;
            font-family: 'Arial Black', sans-serif;
            background-color: rgba(139, 0, 0, 0.6);  /* Rojo oscuro */
            border: 1px solid #FFD700;
            border-radius: 10px;
            padding: 6px 12px;
            text-align: right;
        """)
        
        self.rival_active_pkmHP = QLabel("100% HP", self)
        self.rival_active_pkmHP.setStyleSheet("""
            color: #FFD700;  /* Dorado */
            font-weight: bold;
            font-size: 12px;
            font-family: 'Arial Black', sans-serif;
            background-color: rgba(139, 0, 0, 0.6);  /* Rojo oscuro */
            border: 1px solid #FFD700;
            border-radius: 10px;
            padding: 6px 12px;
            text-align: right;
        """)
        


    def resizeEvent(self, event):
        w = self.width()
        h = self.height()

        # Redimensionar el mapa
        self.map_label.resize(w, h)
        
        # Reposicionar los Pokémon de ambos equipos
        self.position_team_widgets(w, h)

        # Reposicionar el label de logs en posición relativa (0.5, 0.8)
        self.position_log_label(w, h)
        self.position_buttons(w, h)
        self.position_team_preview(w, h)
        self.position_active_pkms(w, h)

    def position_active_pkms(self, w, h):
        # Obtener los paths del pkm ID
        self.team_active_pkmID_path = dataset["pkdex"][str(self.team_active_pkmID)]["sprite"]["back"]
        self.rival_active_pkmID_path = dataset["pkdex"][str(self.rival_active_pkmID)]["sprite"]["front"]
        # Asignar tamaño relativo a la ventana
        increment = 0.5
        widget_size = int(w * increment), int(h * increment)
        # Instanciar los labels
        # Active TEAM
        pos_x_active = 0.05
        pos_y_active = 0.25
        
        movie = QMovie(self.team_active_pkmID_path)
        self.team_active_pkmLabel.setMovie(movie)
        movie.start()
        x = int(w * pos_x_active)
        y = int(h * pos_y_active)
        self.team_active_pkmLabel.resize(*widget_size)
        self.team_active_pkmLabel.move(x, y)
        movie.setScaledSize(self.team_active_pkmLabel.size())
        self.team_active_pkmHP.move(int(w * 0.46), int(h * 0.65))
        # Active Rival
        pos_x_active = 0.4
        pos_y_active = -0.05
        movie = QMovie(self.rival_active_pkmID_path)
        self.rival_active_pkmLabel.setMovie(movie)
        movie.start()
        x = int(w * pos_x_active)
        y = int(h * pos_y_active)
        self.rival_active_pkmLabel.resize(*widget_size)
        self.rival_active_pkmLabel.move(x, y)
        movie.setScaledSize(self.rival_active_pkmLabel.size())
        self.rival_active_pkmHP.move(int(w * 0.81), int(h * 0.35))
        


    def position_team_preview(self, w, h):
        """Posiciona el label del team preview en la posición relativa especificada"""
        # Calcular posición (0.5, 0.8) relativa al tamaño del widget
        label_width = int(w * 0.25)  # del ancho del widget
        label_height = int(h * 0.135)  # del alto del widget
        label_x = int(w * 0.035)
        label_y = int(h * 0.06)
        
        self.teamPreview.resize(label_width, label_height)
        self.teamPreview.move(label_x, label_y)

        label_width_text = int(label_width * 0.5)
        label_height_text = int(label_height * 0.25)
        label_x_text = int(label_x + label_width_text / 2)
        label_y_text = int(label_y - label_height_text)

        self.teamPreviewText.resize(label_width_text, label_height_text)
        self.teamPreviewText.move(label_x_text, label_y_text)
        


    def position_log_label(self, w, h):
        """Posiciona el label de logs en la posición relativa especificada"""
        # Calcular posición (0.5, 0.8) relativa al tamaño del widget
        label_width = int(w * 0.93)  # 80% del ancho del widget
        label_height = int(h * 0.15)  # 10% del alto del widget
        label_x = int(w * 0.035)  # Centrado: (1 - 0.8) / 2 = 0.1
        label_y = int(h * 0.825)  # 80% desde la parte superior
        
        self.labelLog.resize(label_width, label_height)
        self.labelLog.move(label_x, label_y)
        

    def position_buttons(self, w, h):
        """Posiciona los tres botones a la derecha del label"""
        button_width = int(w * 0.15)
        button_height = int(h * 0.07)
        
        # Posición base para los botones (a la derecha del label)
        base_x = int(w * 0.66)  # 0.1 + 0.6 + 0.02 = 0.72
        base_y = int(h * 0.83)
        
        # Posicionar cada botón
        self.btnPastTurn.resize(button_width, button_height)
        self.btnPastTurn.move(base_x, base_y)
        
        self.btnNextTurn.resize(button_width, button_height)
        self.btnNextTurn.move(base_x + button_width, base_y)

        self.btnStartBattle.resize(button_width, button_height)
        self.btnStartBattle.move(base_x, base_y + button_height)

        self.btnEndBattle.resize(button_width, button_height)
        self.btnEndBattle.move(base_x + button_width, base_y + button_height)

    def position_team_widgets(self, w, h):
        """Posiciona los widgets de ambos equipos en el panel"""
        # Calcular tamaño de cada Pokémon
        increment = 0.18
        widget_size = int(w * 0.2 * increment), int(h * 0.3 * increment)
        
        # Posiciones del jugador: empezar en (0.2w, 0.2h) y bajar en intervalos de 0.1 en y
        player_base_x = 0.04
        player_base_y = 0.07
        x_increment = 0.04
        
        # Posicionar Pokémon del jugador (lado izquierdo)
        for i, (widget, movie) in enumerate(self.player_widgets):
            x = int(w * (player_base_x + (i * x_increment)))
            y = int(h * player_base_y)
            
            widget.resize(*widget_size)
            widget.move(x, y)
            movie.setScaledSize(widget.size())
        
        # Posiciones del rival: empezar en (0.8w, 0.2h) y bajar en intervalos de 0.1 en y
        rival_base_x = 0.04
        rival_base_y = 0.135
        
        # Posicionar Pokémon del rival (lado derecho)
        for i, (widget, movie) in enumerate(self.rival_widgets):
            x = int(w * (rival_base_x + (i * x_increment)))
            y = int(h * rival_base_y)
            
            widget.resize(*widget_size)
            widget.move(x, y)
            movie.setScaledSize(widget.size())

    def update_CombatPanel(self, team_index: int, button_text: str = None):
        """Actualiza ambos equipos mostrados según el índice del botón pulsado"""
        # Validar índice del jugador
        if team_index < 0 or team_index >= len(self.teamsPreviewGIFList):
            return
            
        self.current_team_index = team_index
        
        # Limpiar widgets anteriores
        self.clear_team_widgets()
        
        # Crear nuevos widgets para el equipo del jugador
        player_team_gifs = self.teamsPreviewGIFList[team_index]
        for gif_path in player_team_gifs:
            gif_label = QLabel(self)
            movie = QMovie(gif_path)
            gif_label.setMovie(movie)
            movie.start()
            gif_label.show()
            
            self.player_widgets.append((gif_label, movie))
        
        # Crear widgets para el equipo rival (si se proporcionó el botón)
        if button_text and button_text in self.button_to_rival_key:
            rival_key = self.button_to_rival_key[button_text]
            if rival_key in self.rival_teams_gifs:
                rival_team_gifs = self.rival_teams_gifs[rival_key]
                for gif_path in rival_team_gifs:
                    gif_label = QLabel(self)
                    movie = QMovie(gif_path)
                    gif_label.setMovie(movie)
                    movie.start()
                    gif_label.show()
                    
                    self.rival_widgets.append((gif_label, movie))
        
        # Actualizar el texto del log según el team_index
        self.current_team_index = team_index
        self.current_log_index = 0  # Reiniciar índice del log al cambiar de equipo
        self.update_log_text()
        
        # Forzar redibujo y reposicionamiento
        self.update()
        self.resizeEvent(None)

    def update_log_text(self):
        """Actualiza el texto del label de logs según los índices actuales"""
        if (hasattr(self, 'entire_logs') and 
            self.entire_logs and 
            self.current_team_index < len(self.entire_logs) and 
            self.entire_logs[self.current_team_index] and
            self.current_log_index < len(self.entire_logs[self.current_team_index])):
            
            # Obtener el log en la posición actual
            log_text = self.entire_logs[self.current_team_index][self.current_log_index]
            log_text = log_text.split(" : ")
            log_formated = re.sub(r'PLAYER |RIVAL|\(|\)|, |\'|\d+\.\d+', '', str(log_text[0])).strip()
            self.labelLog.setText(log_formated)
            self.team_active_pkmID = log_text[1].split(",")[0]
            self.team_active_pkmHP.setText(log_text[1].split(",")[1] + "% HP")
            self.rival_active_pkmID = log_text[2].split(",")[0]
            self.rival_active_pkmHP.setText(log_text[2].split(",")[1] + "% HP")
            

    def next_turn(self):
        """Avanza al siguiente turno (incrementa el índice del log)"""
        if (hasattr(self, 'entire_logs') and 
            self.entire_logs and 
            self.current_team_index < len(self.entire_logs) and 
            self.entire_logs[self.current_team_index]):
            
            logs_for_team = self.entire_logs[self.current_team_index]
            if self.current_log_index < len(logs_for_team) - 1:
                self.current_log_index += 1
                self.update_log_text()
                self.update_active_pkms()

    def past_turn(self):
        """Retrocede al turno anterior (decrementa el índice del log)"""
        if self.current_log_index > 0:
            self.current_log_index -= 1
            self.update_log_text()
            self.update_active_pkms()

    def start_battle(self):
        """Va al último log del equipo actual"""
        if (hasattr(self, 'entire_logs') and 
            self.entire_logs):
            
            logs_for_team = self.entire_logs[0]
            if logs_for_team:
                self.current_log_index = 0
                self.update_log_text()
                self.update_active_pkms()

    def end_battle(self):
        """Va al último log del equipo actual"""
        if (hasattr(self, 'entire_logs') and 
            self.entire_logs and 
            self.current_team_index < len(self.entire_logs) and 
            self.entire_logs[self.current_team_index]):
            
            logs_for_team = self.entire_logs[self.current_team_index]
            if logs_for_team:
                self.current_log_index = len(logs_for_team) - 1
                self.update_log_text()
                self.update_active_pkms()

    def update_active_pkms(self):
        self.team_active_pkmID_path = dataset["pkdex"][str(self.team_active_pkmID)]["sprite"]["back"]
        self.rival_active_pkmID_path = dataset["pkdex"][str(self.rival_active_pkmID)]["sprite"]["front"]
        movie = QMovie(self.team_active_pkmID_path)
        self.team_active_pkmLabel.setMovie(movie)
        movie.start()
        movie = QMovie(self.rival_active_pkmID_path)
        self.rival_active_pkmLabel.setMovie(movie)
        movie.start()
        # Forzar redibujo y reposicionamiento
        self.update()
        self.resizeEvent(None)

    def clear_team_widgets(self):
        """Elimina todos los widgets de ambos equipos"""
        # Limpiar equipo del jugador
        for widget, movie in self.player_widgets:
            widget.setParent(None)
            movie.stop()
        self.player_widgets = []
        
        # Limpiar equipo rival
        for widget, movie in self.rival_widgets:
            widget.setParent(None)
            movie.stop()
        self.rival_widgets = []

class App(QWidget):
    def __init__(self, individual, feasibility, fitness_value, entire_logs):
        # Preparar el individuo con un equipo por cada combate en la liga
        individual[1] = individual[1] + [individual[1][-1]] * 4
        super().__init__()

        self.pkGIFList = []
        for pkmID in individual[0]:
            if pkmID is None:
                self.pkGIFList.append("./pkm_data/manual_sprites/not_captured.gif")
            else:
                gif_path = dataset["pkdex"][str(pkmID)]["sprite"]["front"]
                self.pkGIFList.append(gif_path)

        self.teamsPreviewGIFList = []
        # Obtener los equipos evolucionados de los logs (primer log)
        for log in entire_logs:
            team_log = log[0][1:-1].split(", ")
            team_trainer = []
            for pkmID in team_log:
                gif_path = str(dataset["pkdex"][str(pkmID)]["sprite"]["front"]).replace("normalized_sprites", "sprites")
                team_trainer.append(gif_path)
            self.teamsPreviewGIFList.append(team_trainer)


        self.setWindowTitle("Fenotipo")
        self.setGeometry(200, 200, 1000, 750)

        # Variables para tracking de selección
        self.selected_main_button = None
        self.selected_sub_buttons = {"mapa": None, "combates": None}

        # --- Layout principal (horizontal) ---
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Menú principal
        self.main_menu = QVBoxLayout()
        self.main_menu.setAlignment(Qt.AlignTop)
        self.main_menu.setSpacing(2)
        self.main_menu.setContentsMargins(5, 10, 5, 10)

        # Crear botones del menú principal
        self.btn_map = QPushButton("MAPA CAPTURAS")
        self.btn_combat = QPushButton("COMBATES")
        
        # Configurar botones principales
        self.btn_map.setObjectName("main_btn")
        self.btn_combat.setObjectName("main_btn")
        self.btn_map.setProperty("selected", False)
        self.btn_combat.setProperty("selected", False)
        
        # Conectar señales
        self.btn_map.clicked.connect(lambda: self.show_submenu("mapa", individual=individual))
        self.btn_combat.clicked.connect(lambda: self.show_submenu("combates", individual=individual))

        self.main_menu.addWidget(self.btn_map)
        self.main_menu.addWidget(self.btn_combat)

        # Empujar al final
        self.main_menu.addStretch(1)

        # Labels al fondo de valores del individuo
        if feasibility:
            label1 = QLabel("Factible")
        else:
            label1 = QLabel(f"No Factible")
        label2 = QLabel("Valor Fitness: " + str(fitness_value))

        label1.setFont(QFont("Arial", 12))
        label1.setStyleSheet("color: white; font-weight: bold;")
        label2.setFont(QFont("Arial", 12))
        label2.setStyleSheet("color: white; font-weight: bold;")

        self.main_menu.addWidget(label1)
        self.main_menu.addWidget(label2)

        main_menu_widget = QWidget()
        main_menu_widget.setLayout(self.main_menu)
        main_menu_widget.setObjectName("main_menu")
        main_menu_widget.setFixedWidth(190)

        # ===== SUBMENÚ (dinámico con QStackedWidget) =====
        self.submenu_stack = QStackedWidget()
        self.submenu_stack.setFixedWidth(190)

        # Diccionario para almacenar botones de submenú
        self.submenu_buttons = {"mapa": [], "combates": []}

        # Submenú de mapas
        submenu_map = QWidget()
        submenu_map_layout = QVBoxLayout()
        submenu_map_layout.setAlignment(Qt.AlignTop)
        submenu_map_layout.setSpacing(2)
        submenu_map_layout.setContentsMargins(5, 10, 5, 10)
        submenu_map.setObjectName("submenu_map")
        
        map_buttons = [
            "MAPA COMPLETO", "RIVAL RUTA 22", "GYM PLATEADA", "RIVAL CELESTE", "GYM CELESTE", "RIVAL CARMIN", "GYM CARMIN", "RIVAL TORRE PKM", "GYM AZULONA",
            "GIOVANNI AZULONA", "RIVAL AZAFRAN", "GIOVANNI AZAFRAN", "GYM FUCSIA", "GYM AZAFRAN",
            "GYM CANELA", "GYM VERDE", "RIVAL VERDE", "LIGA POKÉMON"
        ]
        
        for name in map_buttons:
            btn = QPushButton(name)
            btn.setObjectName("sub_btn")
            btn.setProperty("selected", False)
            btn.clicked.connect(lambda checked, btn=btn, menu_type="mapa", name=name: self.select_sub_button_mapa(btn, menu_type, name, individual))
            submenu_map_layout.addWidget(btn)
            self.submenu_buttons["mapa"].append(btn)
            
        submenu_map.setLayout(submenu_map_layout)

        # Submenú de combates
        submenu_combat = QWidget()
        submenu_combat_layout = QVBoxLayout()
        submenu_combat_layout.setAlignment(Qt.AlignTop)
        submenu_combat_layout.setSpacing(2)
        submenu_combat_layout.setContentsMargins(5, 10, 5, 10)
        submenu_combat.setObjectName("submenu_combat")
        
        combat_buttons = [
            "RIVAL RUTA 22", "GYM PLATEADA", "RIVAL CELESTE", "GYM CELESTE", "RIVAL CARMIN", "GYM CARMIN", "RIVAL TORRE PKM", "GYM AZULONA",
            "GIOVANNI AZULONA", "RIVAL AZAFRAN", "GIOVANNI AZAFRAN", "GYM FUCSIA", "GYM AZAFRAN",
            "GYM CANELA", "GYM VERDE", "RIVAL VERDE", "ALTO MANDO LORELEI", "ALTO MANDO BRUNO",
            "ALTO MANDO AGATHA", "ALTO MANDO LANCE", "RIVAL CAMPEON"
        ]
        
        for name in combat_buttons:
            btn = QPushButton(name)
            btn.setObjectName("sub_btn")
            btn.setProperty("selected", False)
            btn.clicked.connect(lambda checked, btn=btn, menu_type="combates": self.select_sub_button(btn, menu_type))
            submenu_combat_layout.addWidget(btn)
            self.submenu_buttons["combates"].append(btn)
            
        submenu_combat.setLayout(submenu_combat_layout)

        # Añadir al stack
        self.submenu_stack.addWidget(submenu_map)      # index 0
        self.submenu_stack.addWidget(submenu_combat)   # index 1

        # PANEL CENTRAL
        self.central_stack = QStackedWidget()

        # Panel de mapas
        self.map_panel = MapPanel(self.pkGIFList)

        # Panel de combates
        self.combat_panel = CombatPanel(self.teamsPreviewGIFList, prepare_entire_logs(entire_logs), starterID=individual[0][0])

        # Añadir al stack
        self.central_stack.addWidget(self.map_panel)    # index 0
        self.central_stack.addWidget(self.combat_panel) # index 1

        # Añadir al layout principal
        layout.addWidget(main_menu_widget)
        layout.addWidget(self.submenu_stack)
        layout.addWidget(self.central_stack, stretch=1)

        # Mostrar por defecto el menú de mapa y seleccionar opciones por defecto
        self.show_submenu("mapa", individual=individual)

        self.setStyleSheet(STYLE_SHEET)

    def show_submenu(self, menu_type, individual):
        """Muestra el submenú correspondiente y actualiza selección del botón principal"""
        # Resetear selección anterior del menú principal
        if self.selected_main_button:
            self.selected_main_button.setProperty("selected", False)
            self.selected_main_button.style().unpolish(self.selected_main_button)
            self.selected_main_button.style().polish(self.selected_main_button)
        
        # Seleccionar nuevo botón principal
        if menu_type == "mapa":
            self.submenu_stack.setCurrentIndex(0)
            self.central_stack.setCurrentIndex(0)   # panel central = MapPanel
            self.selected_main_button = self.btn_map
            
            # Forzar siempre selección del predeterminado "MAPA COMPLETO"
            self.select_sub_button_mapa(
                self.submenu_buttons["mapa"][0], "mapa", "MAPA COMPLETO",
                individual=individual, force_select=True
            )
        elif menu_type == "combates":
            self.submenu_stack.setCurrentIndex(1)
            self.central_stack.setCurrentIndex(1)   # panel central = CombatPanel
            self.selected_main_button = self.btn_combat
            
            # Forzar siempre selección del predeterminado "GYM PLATEADA"
            default_button = self.submenu_buttons["combates"][0]
            self.select_sub_button(
                default_button, 
                "combates",
                force_select=True
            )
            # Asegurar que se muestre el equipo 0
            self.combat_panel.update_CombatPanel(0, default_button.text())
        
        # Aplicar estilo al botón principal seleccionado
        if self.selected_main_button:
            self.selected_main_button.setProperty("selected", True)
            self.selected_main_button.style().unpolish(self.selected_main_button)
            self.selected_main_button.style().polish(self.selected_main_button)

    def select_sub_button_mapa(self, button, menu_type, name, individual, force_select=False):
        """Selecciona un botón del submenú"""
        # Si el botón ya está seleccionado y no es forzado, no hacer nada (no deseleccionar)
        if button.property("selected") and not force_select:
            return
            
        # Resetear selección anterior en este submenú
        for btn in self.submenu_buttons[menu_type]:
            if btn != button:
                btn.setProperty("selected", False)
                btn.style().unpolish(btn)
                btn.style().polish(btn)
        
        # Seleccionar el nuevo botón
        button.setProperty("selected", True)
        button.style().unpolish(button)
        button.style().polish(button)
        
        # Actualizar referencia al botón seleccionado
        self.selected_sub_buttons[menu_type] = button
        
        self.pkGIFList = []
        if(name == "MAPA COMPLETO" or name == "LIGA POKÉMON"):
            previous_routes_key = "ALTO_MANDO_LANCE"
        else:
            previous_routes_key = name.replace(" ", "_")
        for i in range(0, len(individual[0])):
            if PREVIOUS_ROUTES_TO_TRAINER[previous_routes_key] <= i:
                self.pkGIFList.append("./pkm_data/manual_sprites/not_captured_yet.gif")
            elif individual[0][i] is None:
                self.pkGIFList.append("./pkm_data/manual_sprites/not_captured.gif")
            else:
                gif_path = dataset["pkdex"][str(individual[0][i])]["sprite"]["front"]
                self.pkGIFList.append(gif_path)
        

        self.map_panel.update_MapPanel(self.pkGIFList)


    def select_sub_button(self, button, menu_type, force_select=False):
        """Selecciona un botón del submenú"""
        # Si el botón ya está seleccionado y no es forzado, no hacer nada (no deseleccionar)
        if button.property("selected") and not force_select:
            return
            
        # Resetear selección anterior en este submenú
        for btn in self.submenu_buttons[menu_type]:
            if btn != button:
                btn.setProperty("selected", False)
                btn.style().unpolish(btn)
                btn.style().polish(btn)
        
        # Seleccionar el nuevo botón
        button.setProperty("selected", True)
        button.style().unpolish(button)
        button.style().polish(button)
        
        # Actualizar referencia al botón seleccionado
        self.selected_sub_buttons[menu_type] = button
        
        # Obtener el índice del botón pulsado en la lista de combates
        combat_buttons = [
            "RIVAL RUTA 22", "GYM PLATEADA", "RIVAL CELESTE", "GYM CELESTE", "RIVAL CARMIN", "GYM CARMIN", "RIVAL TORRE PKM", "GYM AZULONA",
            "GIOVANNI AZULONA", "RIVAL AZAFRAN", "GIOVANNI AZAFRAN", "GYM FUCSIA", "GYM AZAFRAN",
            "GYM CANELA", "GYM VERDE", "RIVAL VERDE", "ALTO MANDO LORELEI", "ALTO MANDO BRUNO",
            "ALTO MANDO AGATHA", "ALTO MANDO LANCE", "RIVAL CAMPEON"
        ]
        
        # Encontrar el índice del botón en la lista
        button_text = button.text()
        if button_text in combat_buttons:
            team_index = combat_buttons.index(button_text)
            # Actualizar el CombatPanel con ambos equipos
            self.combat_panel.update_CombatPanel(team_index, button_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    individual = generate_individual()
    (feasibility, fitness_value, entire_logs) = calculate_fitness(individual, dataset=dataset, verbose=False)
    window = App(individual, feasibility, fitness_value, entire_logs)
    window.show()
    sys.exit(app.exec_())