"""
Fenêtre principale de l'application.
"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QPushButton,
    QStackedWidget,
)
from PySide6.QtCore import Qt

from ui.dashboard.dashboard_widget import DashboardWidget
from ui.eleves.eleves_widget import ElevesWidget
from ui.recus.recu_viewer import RecusViewerWidget


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application."""

    def __init__(self, conn):
        """
        Initialise la fenêtre principale.

        Args:
            conn: Connexion SQLite à utiliser.
        """
        super().__init__()
        self.conn = conn
        self.setWindowTitle("Gestion Scolarité")
        self.setMinimumSize(1000, 700)

        # Créer le widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Barre latérale
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)

        # Zone de contenu
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, stretch=1)

        # Créer les widgets des pages
        self.dashboard_widget = DashboardWidget(self.conn)
        self.eleves_widget = ElevesWidget(self.conn)
        self.recus_widget = RecusViewerWidget(self.conn)

        # Ajouter les widgets au stacked widget
        self.stacked_widget.addWidget(self.dashboard_widget)
        self.stacked_widget.addWidget(self.eleves_widget)
        self.stacked_widget.addWidget(self.recus_widget)

        # Boutons de navigation
        self.nav_buttons = {
            "dashboard": self.sidebar_buttons[0],
            "eleves": self.sidebar_buttons[1],
            "recus": self.sidebar_buttons[2],
        }

        # Connecter les boutons
        self.sidebar_buttons[0].clicked.connect(lambda: self.show_page("dashboard"))
        self.sidebar_buttons[1].clicked.connect(lambda: self.show_page("eleves"))
        self.sidebar_buttons[2].clicked.connect(lambda: self.show_page("recus"))

        # Afficher le dashboard par défaut
        self.show_page("dashboard")

    def _create_sidebar(self) -> QFrame:
        """
        Crée la barre latérale de navigation.

        Returns:
            Frame contenant la barre latérale.
        """
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(5)

        # Titre
        title = QPushButton("Gestion Scolarité")
        title.setCheckable(False)
        title.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border: none;
                color: white;
                padding: 20px;
                font-size: 16px;
                font-weight: bold;
                text-align: center;
            }
        """
        )
        layout.addWidget(title)

        layout.addSpacing(20)

        # Boutons de navigation
        self.sidebar_buttons = []

        btn_dashboard = QPushButton("📊 Tableau de bord")
        btn_dashboard.setCheckable(True)
        btn_dashboard.setObjectName("navButton")
        self.sidebar_buttons.append(btn_dashboard)
        layout.addWidget(btn_dashboard)

        btn_eleves = QPushButton("👨‍🎓 Élèves")
        btn_eleves.setCheckable(True)
        btn_eleves.setObjectName("navButton")
        self.sidebar_buttons.append(btn_eleves)
        layout.addWidget(btn_eleves)

        btn_recus = QPushButton("📄 Reçus")
        btn_recus.setCheckable(True)
        btn_recus.setObjectName("navButton")
        self.sidebar_buttons.append(btn_recus)
        layout.addWidget(btn_recus)

        layout.addStretch()

        return sidebar

    def show_page(self, page_name: str) -> None:
        """
        Affiche une page spécifique.

        Args:
            page_name: Nom de la page ("dashboard", "eleves" ou "recus").
        """
        if page_name == "dashboard":
            self.stacked_widget.setCurrentWidget(self.dashboard_widget)
            self.nav_buttons["dashboard"].setChecked(True)
            self.nav_buttons["eleves"].setChecked(False)
            self.nav_buttons["recus"].setChecked(False)
        elif page_name == "eleves":
            self.stacked_widget.setCurrentWidget(self.eleves_widget)
            self.nav_buttons["dashboard"].setChecked(False)
            self.nav_buttons["eleves"].setChecked(True)
            self.nav_buttons["recus"].setChecked(False)
        elif page_name == "recus":
            self.stacked_widget.setCurrentWidget(self.recus_widget)
            self.nav_buttons["dashboard"].setChecked(False)
            self.nav_buttons["eleves"].setChecked(False)
            self.nav_buttons["recus"].setChecked(True)
