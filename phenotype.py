import base64
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget
from PyQt5.QtGui import QPixmap, QMovie, QFont
from PyQt5.QtCore import Qt
import requests
from io import BytesIO
from tempfile import NamedTemporaryFile
from battle_simulator import dataset
from individual import INDIVIDUAL

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
    (0.204, 0.719), # PUEBLO PALETA
    (0.204, 0.625), # RUTA 1
    (0.122, 0.545), # RUTA 22
    (0.204, 0.49), # RUTA 2
    (0.204, 0.41), # BOSQUE VERDE
    (0.285, 0.327), # RUTA 3
    (0.51, 0.27), # RUTA 4
    (0.41, 0.27), # MONTE MOON
    (0.62, 0.208), # RUTA 24
    (0.7, 0.16), # RUTA 25
    (0.62, 0.3495), # RUTA 5
    (0.62, 0.518), # RUTA 6
    (0.726, 0.605), # RUTA 11
    (0.662, 0.605), # CUEVA DIGLETT
    (0.7, 0.27), # RUTA 9
    (0.787, 0.376), # RUTA 10
    (0.787, 0.27), # TUNEL ROCA
    (0.7, 0.44), # RUTA 8
    (0.555, 0.44), # RUTA 7
    (0.41, 0.44), # RUTA 16
    (0.787, 0.44), # TORRE POKEMON
    (0.787, 0.605), # RUTA 12
    (0.726, 0.718), # RUTA 13
    (0.662, 0.718), # RUTA 14
    (0.62, 0.775), # RUTA 15
    (0.537, 0.775), # ZONA SAFARI
    (0.41, 0.775), # RUTA 18
    (0.33, 0.605), # RUTA 17
    (0.537, 0.885), # RUTA 19
    (0.45, 0.885), # RUTA 20
    (0.204, 0.795), # RUTA 21
    (0.36, 0.885), # ISLAS ESPUMA
    (0.204, 0.885), # MANSION PKM
    (0.787, 0.323), # CENTRAL ENERGIA
    (0.122, 0.44), # RUTA 23
    (0.122, 0.327), # CALLE VICTORIA
]

class MapPanel(QWidget):
    def __init__(self, pkGIFList: list):
        super().__init__()

        self.setMouseTracking(True)
        self.normalize = False
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
        if self.normalize:
            reducer_gif = 1.1
        else:
            reducer_gif = 0.75
        widget_size = int(w * 0.075 * reducer_gif), int(h * 0.1 * reducer_gif)

        for i, (widget, movie) in enumerate(self.route_widgets):
            if self.normalize:
                x = int(w * (PK_POSITIONS[i][0]- 0.028))
                y = int(h * (PK_POSITIONS[i][1]- 0.088))
            else: 
                x = int(w * PK_POSITIONS[i][0])
                y = int(h * (PK_POSITIONS[i][1] - 0.005))

            widget.move(x, y)
            widget.resize(*widget_size)
            movie.setScaledSize(widget.size())

        # --- Texto general ---
        self.text_label.move(int(w * self.pos_text[0]), int(h * self.pos_text[1]))
        font_size = max(int(h * 0.03), 8)  # fuente proporcional a la altura
        self.text_label.setFont(QFont("Arial", font_size))
        self.text_label.adjustSize()

    def update_MapPanel(self, pkGIFList: list):
        """Actualiza la lista de sprites mostrados en el mapa"""
        # Eliminar los widgets anteriores
        print(pkGIFList)
        for widget, movie in self.route_widgets:
            widget.setParent(None)
            movie.stop()

        self.route_widgets = []

        # Crear los nuevos
        for pkGIF in pkGIFList:
            gif_label = QLabel(self)
            movie = QMovie(pkGIF)
            gif_label.setMovie(movie)
            movie.start()
            gif_label.show()
            self.route_widgets.append((gif_label, movie))

        # Forzar redibujo y reposicionamiento
        self.update()
        self.resizeEvent(None)

class App(QWidget):
    def __init__(self, individual):
        super().__init__()

        self.pkGIFList = []
        for pkmID in individual[0]:
            if pkmID is None:
                self.pkGIFList.append("./pkm_data/sprites/pokeball_loading.gif")
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

        # ===== MENÚ PRINCIPAL =====
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
        self.btn_map.clicked.connect(lambda: self.show_submenu("mapa"))
        self.btn_combat.clicked.connect(lambda: self.show_submenu("combates"))

        self.main_menu.addWidget(self.btn_map)
        self.main_menu.addWidget(self.btn_combat)

        main_menu_widget = QWidget()
        main_menu_widget.setLayout(self.main_menu)
        main_menu_widget.setObjectName("main_menu")
        main_menu_widget.setFixedWidth(200)

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
            "GYM CANELA", "GYM VERDE", "LIGA POKEMON"
        ]
        
        for name in map_buttons:
            btn = QPushButton(name)
            btn.setObjectName("sub_btn")
            btn.setProperty("selected", False)
            btn.clicked.connect(lambda checked, btn=btn, menu_type="mapa", name=name: self.select_sub_button_mapa(btn, menu_type, name))
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
        self.map_panel = MapPanel(self.pkGIFList)

        # Añadir al layout principal
        layout.addWidget(main_menu_widget)
        layout.addWidget(self.submenu_stack)
        layout.addWidget(self.map_panel, stretch=1)

        # Mostrar por defecto el menú de mapa y seleccionar opciones por defecto
        self.show_submenu("mapa")

        self.setStyleSheet(STYLE_SHEET)

    def show_submenu(self, menu_type):
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
            
            # Seleccionar automáticamente "MAPA COMPLETO" si no hay nada seleccionado
            if not self.selected_sub_buttons["mapa"]:
                self.select_sub_button_mapa(self.submenu_buttons["mapa"][0], "mapa", "MAPA COMPLETO", force_select=True)
                
        elif menu_type == "combates":
            self.submenu_stack.setCurrentIndex(1)
            self.selected_main_button = self.btn_combat
            
            # Seleccionar automáticamente "GYM PLATEADA" si no hay nada seleccionado
            if not self.selected_sub_buttons["combates"]:
                self.select_sub_button(self.submenu_buttons["combates"][0], "combates", force_select=True)
        
        # Aplicar estilo al botón principal seleccionado
        if self.selected_main_button:
            self.selected_main_button.setProperty("selected", True)
            self.selected_main_button.style().unpolish(self.selected_main_button)
            self.selected_main_button.style().polish(self.selected_main_button)

    def select_sub_button_mapa(self, button, menu_type, name, force_select=False):
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
        
        print(name)
        if(name == "GYM PLATEADA"):
            self.pkGIFList = []
            for pkmID in INDIVIDUAL[0]:
                self.pkGIFList.append("./pkm_data/sprites/pokeball_loading.gif")

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
            self.pkGIFList.append("./pkm_data/sprites/pokeball_loading.gif")

        self.map_panel.update_MapPanel(self.pkGIFList)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App(INDIVIDUAL)
    window.show()
    sys.exit(app.exec_())