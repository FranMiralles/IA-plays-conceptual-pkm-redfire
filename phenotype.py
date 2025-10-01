import base64
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget
from PyQt5.QtGui import QPixmap, QMovie, QFont
from PyQt5.QtCore import Qt
import requests
from io import BytesIO
from tempfile import NamedTemporaryFile
from battle_simulator import *
from individual import INDIVIDUAL_EXAMPLE
from route_data.trainers import PREVIOUS_ROUTES_TO_TRAINER, TRAINERS_ORDER

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
                border-radius: 6px;
                padding: 12px 15px;
                font-weight: bold;
                text-align: left;
                margin: 2px;
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
                border-radius: 4px;
                padding: 10px 12px;
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
                border-left: 3px solid #c0392b;
            }
            
            /* Efectos generales para botones */
            QPushButton:pressed {
                background-color: #16a085;
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
    def __init__(self, teamsGIFList: list):
        super().__init__()

        self.setMouseTracking(True)
        # --- Imagen base ---
        self.map_label = QLabel(self)
        self.pixmap = QPixmap("images/forest.png")
        self.map_label.setPixmap(self.pixmap)
        self.map_label.setScaledContents(True)
        
        # Lista de equipos del jugador (cada equipo es una lista de GIFs)
        self.teamsGIFList = teamsGIFList
        self.current_team_index = 0
        
        # Definir equipos rivales (pkmID)
        self.rival_teams = {
            "GYM_PLATEADA": [74, 95],
            "GYM_CELESTE": [120, 121],
            "GYM_CARMIN": [100, 25, 26],
            "GYM_AZULONA": [71, 114, 45],
            "GIOVANNI_AZULONA": [95, 111, 115],
            "GIOVANNI_AZAFRAN": [33, 111, 115, 31],
            "GYM_FUCSIA": [109, 109, 89, 110],
            "GYM_AZAFRAN": [64, 49, 122, 65],
            "GYM_CANELA": [58, 77, 78, 59],
            "GYM_VERDE": [111, 51, 34, 31, 111],
            "ALTO_MANDO_LORELEI": [87, 91, 80, 124, 131],
            "ALTO_MANDO_BRUNO": [95, 107, 106, 95, 68],
            "ALTO_MANDO_AGATHA": [94, 42, 93, 24, 94],
            "ALTO_MANDO_LANCE": [130, 148, 148, 142, 149]
        }
        
        # Convertir IDs rivales a GIFs
        self.rival_teams_gifs = {}
        for trainer, team_ids in self.rival_teams.items():
            gif_team = []
            for pkm_id in team_ids:
                gif_path = dataset["pkdex"][str(pkm_id)]["sprite"]["front"]
                gif_team.append(gif_path)
            self.rival_teams_gifs[trainer] = gif_team
        
        # Mapeo de nombres de botones a claves de equipos rivales
        self.button_to_rival_key = {
            "GYM PLATEADA": "GYM_PLATEADA",
            "GYM CELESTE": "GYM_CELESTE", 
            "GYM CARMIN": "GYM_CARMIN",
            "GYM AZULONA": "GYM_AZULONA",
            "GIOVANNI AZULONA": "GIOVANNI_AZULONA",
            "GIOVANNI AZAFRAN": "GIOVANNI_AZAFRAN",
            "GYM FUCSIA": "GYM_FUCSIA",
            "GYM AZAFRAN": "GYM_AZAFRAN",
            "GYM CANELA": "GYM_CANELA",
            "GYM VERDE": "GYM_VERDE",
            "ALTO MANDO LORELEI": "ALTO_MANDO_LORELEI",
            "ALTO MANDO BRUNO": "ALTO_MANDO_BRUNO",
            "ALTO MANDO AGATHA": "ALTO_MANDO_AGATHA",
            "ALTO MANDO LANCE": "ALTO_MANDO_LANCE"
        }
        
        # Listas para almacenar los widgets de Pokémon
        self.player_widgets = []
        self.rival_widgets = []

    def resizeEvent(self, event):
        w = self.width()
        h = self.height()

        # Redimensionar el mapa
        self.map_label.resize(w, h)
        
        # Reposicionar los Pokémon de ambos equipos
        self.position_team_widgets(w, h)

    def position_team_widgets(self, w, h):
        """Posiciona los widgets de ambos equipos en el panel"""
        # Calcular tamaño de cada Pokémon
        widget_size = int(w * 0.2), int(h * 0.3)
        
        # Posiciones del jugador: empezar en (0.2w, 0.2h) y bajar en intervalos de 0.1 en y
        player_base_x = 0.25
        player_base_y = -0.1
        y_increment = 0.14
        
        # Posicionar Pokémon del jugador (lado izquierdo)
        for i, (widget, movie) in enumerate(self.player_widgets):
            x = int(w * player_base_x)
            y = int(h * (player_base_y + (i * y_increment)))
            
            widget.resize(*widget_size)
            widget.move(x, y)
            movie.setScaledSize(widget.size())
        
        # Posiciones del rival: empezar en (0.8w, 0.2h) y bajar en intervalos de 0.1 en y
        rival_base_x = 0.45
        rival_base_y = -0.1
        
        # Posicionar Pokémon del rival (lado derecho)
        for i, (widget, movie) in enumerate(self.rival_widgets):
            x = int(w * rival_base_x)
            y = int(h * (rival_base_y + (i * y_increment)))
            
            widget.resize(*widget_size)
            widget.move(x, y)
            movie.setScaledSize(widget.size())

    def update_CombatPanel(self, team_index: int, button_text: str = None):
        """Actualiza ambos equipos mostrados según el índice del botón pulsado"""
        # Validar índice del jugador
        if team_index < 0 or team_index >= len(self.teamsGIFList):
            return
            
        self.current_team_index = team_index
        
        # Limpiar widgets anteriores
        self.clear_team_widgets()
        
        # Crear nuevos widgets para el equipo del jugador
        player_team_gifs = self.teamsGIFList[team_index]
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
        super().__init__()

        self.pkGIFList = []
        for pkmID in individual[0]:
            if pkmID is None:
                self.pkGIFList.append("./pkm_data/manual_sprites/not_captured.gif")
            else:
                gif_path = dataset["pkdex"][str(pkmID)]["sprite"]["front"]
                self.pkGIFList.append(gif_path)

        self.teamsGIFList = []
        for team in individual[1]:
            team_trainer = []
            for pkmID in team:
                gif_path = dataset["pkdex"][str(pkmID)]["sprite"]["front"]
                team_trainer.append(gif_path)
            self.teamsGIFList.append(team_trainer)


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
            "MAPA COMPLETO", "GYM PLATEADA", "GYM CELESTE", "GYM CARMIN", "GYM AZULONA",
            "GIOVANNI AZULONA", "GIOVANNI AZAFRAN", "GYM FUCSIA", "GYM AZAFRAN",
            "GYM CANELA", "GYM VERDE", "LIGA POKÉMON"
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
            "GYM PLATEADA", "GYM CELESTE", "GYM CARMIN", "GYM AZULONA",
            "GIOVANNI AZULONA", "GIOVANNI AZAFRAN", "GYM FUCSIA", "GYM AZAFRAN",
            "GYM CANELA", "GYM VERDE", "ALTO MANDO LORELEI", "ALTO MANDO BRUNO",
            "ALTO MANDO AGATHA", "ALTO MANDO LANCE"
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

        # PANEL CENTRAL (StackedWidget con MapPanel y CombatPanel)
        self.central_stack = QStackedWidget()

        # Panel de mapas
        self.map_panel = MapPanel(self.pkGIFList)

        # Panel de combates
        self.combat_panel = CombatPanel(self.teamsGIFList)  # <- tu widget CombatPanel

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
            "GYM PLATEADA", "GYM CELESTE", "GYM CARMIN", "GYM AZULONA",
            "GIOVANNI AZULONA", "GIOVANNI AZAFRAN", "GYM FUCSIA", "GYM AZAFRAN",
            "GYM CANELA", "GYM VERDE", "ALTO MANDO LORELEI", "ALTO MANDO BRUNO",
            "ALTO MANDO AGATHA", "ALTO MANDO LANCE"
        ]
        
        # Encontrar el índice del botón en la lista
        button_text = button.text()
        if button_text in combat_buttons:
            team_index = combat_buttons.index(button_text)
            # Actualizar el CombatPanel con ambos equipos
            self.combat_panel.update_CombatPanel(team_index, button_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    (feasibility, fitness_value, entire_logs) = calculate_fitness(INDIVIDUAL_EXAMPLE, dataset=dataset, verbose=False)
    window = App(INDIVIDUAL_EXAMPLE, feasibility, fitness_value, entire_logs)
    print("FITNESS VALUE")
    print(fitness_value)
    window.show()
    sys.exit(app.exec_())