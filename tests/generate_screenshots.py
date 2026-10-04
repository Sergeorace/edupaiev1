"""
Script pour générer des captures d'écran de l'UI en mode offscreen.
"""

import os
import sys
from pathlib import Path

# Mode offscreen
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

import sqlite3
from database.database import create_connection, init_database
from ui.main_window import MainWindow


def generate_screenshots():
    """Génère des captures d'écran de l'application."""
    # Initialiser la base de données si nécessaire
    db_path = Path(__file__).parent.parent / "school.db"
    if not db_path.exists():
        init_database()

    # Créer l'application
    app = QApplication([])
    app.setApplicationName("Gestion Scolarité")

    # Créer la connexion
    conn = create_connection()

    # Créer la fenêtre
    window = MainWindow(conn)
    window.show()

    # Forcer le rendu
    app.processEvents()

    # Créer le dossier des captures
    screenshots_dir = Path(__file__).parent.parent / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)

    # Capturer le dashboard
    window.show_page("dashboard")
    app.processEvents()
    pixmap = window.grab()
    pixmap.save(str(screenshots_dir / "dashboard.png"))
    print(f"Capture enregistrée: {screenshots_dir / 'dashboard.png'}")

    # Capturer la page élèves
    window.show_page("eleves")
    app.processEvents()
    pixmap = window.grab()
    pixmap.save(str(screenshots_dir / "eleves.png"))
    print(f"Capture enregistrée: {screenshots_dir / 'eleves.png'}")

    conn.close()
    app.quit()


if __name__ == "__main__":
    generate_screenshots()
