import base64
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget
from PyQt5.QtGui import QPixmap, QMovie, QFont
from PyQt5.QtCore import Qt
import requests
from io import BytesIO
from tempfile import NamedTemporaryFile
from battle_simulator import *
from individual import INDIVIDUAL
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
    "RUTA 10", "TUNEL ROCA", "RUTA 8", "RUTA 7", "RUTA 16",
    "TORRE POKEMON", "RUTA 12", "RUTA 13", "RUTA 14", "RUTA 15",
    "ZONA SAFARI", "RUTA 18", "RUTA 17", "RUTA 19", "RUTA 20",
    "RUTA 21", "ISLAS ESPUMA", "MANSION PKM", "CENTRAL ENERGIA",
    "RUTA 23", "CALLE VICTORIA"
]

def select_direction(route_name: str):
    if route_name in ["PUEBLO PALETA", "RUTA 1", "RUTA 21", "MANSION PKM", "RUTA 5", "RUTA 6", "RUTA 14"]:
        return "left"
        pass

class MapPanel(QWidget):
    def __init__(self, pkGIFList: list, feasibility: bool):
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
                self.route_widgets.append((gif_label, movie, "ball", name_label))
            else:
                self.route_widgets.append((gif_label, movie, "pkm", name_label))

        # --- Texto ---
        if feasibility:
            self.text_label = QLabel("Individuo: Factible", self)
        else:
            self.text_label = QLabel("Individuo: No factible", self)

        self.text_label.setStyleSheet("color: white; background-color: rgba(0,0,0,150); padding: 4px;")
        self.pos_text = (0, 0)

    def resizeEvent(self, event):
        w = self.width()
        h = self.height()

        # Redimensionar el mapa
        self.map_label.resize(w, h)

        # Calcular tamaño relativo para los GIFs / labels
        increment_gif = 1
        #widget_size_ball = int(w * 0.1 * reducer_gif), int(h * 0.15 * reducer_gif)
        widget_size_pkm = int(w * 0.1 * increment_gif), int(h * 0.15 * increment_gif)

        for i, (widget, movie, type, name_label) in enumerate(self.route_widgets):
            if type == "pkm":
                x = int(w * PK_POSITIONS[i][0])
                y = int(h * PK_POSITIONS[i][1])
                name_label.move(int(x - name_label.width() + w * 0.02), int(y - name_label.height() + h * 0.15))
            else:
                x = int(w * PK_POSITIONS[i][0])
                y = int(h * (PK_POSITIONS[i][1] + 0.05))
                name_label.move(int(x - name_label.width() + w * 0.02), int(y - name_label.height() + h * 0.1))

            widget.resize(*widget_size_pkm)
            widget.move(x, y)
            movie.setScaledSize(widget.size())

            # Label a la izquierda del GIF
            #name_label.move(x - name_label.width(), y + widget.height()//2 - name_label.height()//2)
            
            font_size = max(int(h * 0.02), 7)
            name_label.setFont(QFont("Arial", font_size))
            name_label.adjustSize()

        # --- Texto general ---
        self.text_label.move(int(w * self.pos_text[0]), int(h * self.pos_text[1]))
        font_size = max(int(h * 0.03), 8)  # fuente proporcional a la altura
        self.text_label.setFont(QFont("Arial", font_size))
        self.text_label.adjustSize()

    def update_MapPanel(self, pkGIFList: list):
        """Actualiza la lista de sprites mostrados en el mapa"""
        # Eliminar los widgets anteriores
        for widget, movie, type, name_label in self.route_widgets:
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

            if pkGIF in ["./pkm_data/manual_sprites/not_captured.gif",
                        "./pkm_data/manual_sprites/not_captured_yet.gif"]:
                self.route_widgets.append((gif_label, movie, "ball", name_label))
            else:
                self.route_widgets.append((gif_label, movie, "pkm", name_label))

        # Forzar redibujo y reposicionamiento
        self.update()
        self.resizeEvent(None)

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

        main_menu_widget = QWidget()
        main_menu_widget.setLayout(self.main_menu)
        main_menu_widget.setObjectName("main_menu")
        main_menu_widget.setFixedWidth(180)

        # ===== SUBMENÚ (dinámico con QStackedWidget) =====
        self.submenu_stack = QStackedWidget()
        self.submenu_stack.setFixedWidth(180)

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

        # ===== PANEL CENTRAL =====
        self.map_panel = MapPanel(self.pkGIFList, feasibility)

        # Añadir al layout principal
        layout.addWidget(main_menu_widget)
        layout.addWidget(self.submenu_stack)
        layout.addWidget(self.map_panel, stretch=1)

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
            self.selected_main_button = self.btn_map
            
            # Forzar siempre selección del predeterminado "MAPA COMPLETO"
            self.select_sub_button_mapa(
                self.submenu_buttons["mapa"][0], "mapa", "MAPA COMPLETO",
                individual=individual, force_select=True
            )
                        
        elif menu_type == "combates":
            self.submenu_stack.setCurrentIndex(1)
            self.selected_main_button = self.btn_combat
            
            # Forzar siempre selección del predeterminado "GYM PLATEADA"
            self.select_sub_button(
                self.submenu_buttons["combates"][0], "combates",
                force_select=True
            )
        
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
        


        self.pkGIFList = []
        for pkmID in INDIVIDUAL[0]:
            self.pkGIFList.append("./pkm_data/manual_sprites/not_captured.gif")

        self.map_panel.update_MapPanel(self.pkGIFList)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    (feasibility, fitness_value, entire_logs) = calculate_fitness(INDIVIDUAL, dataset=dataset, verbose=False)
    window = App(INDIVIDUAL, feasibility, fitness_value, entire_logs)
    print("FITNESS VALUE")
    print(fitness_value)
    window.show()
    sys.exit(app.exec_())