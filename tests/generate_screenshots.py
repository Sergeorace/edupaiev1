"""
Script pour générer des captures d'écran de l'UI en mode offscreen.
"""

import os
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QFontDatabase

from database.database import create_connection, init_database
from main import load_stylesheet
from ui.main_window import MainWindow


def generate_screenshots() -> None:
    """Génère les captures des trois écrans principaux en mode offscreen."""
    project_dir = Path(__file__).resolve().parents[1]
    db_path = project_dir / "school.db"
    if not db_path.exists():
        init_database(db_path)

    app = QApplication.instance() or QApplication([])
    app.setApplicationName("Gestion Scolarité")
    font_path = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "arial.ttf"
    if font_path.exists():
        font_id = QFontDatabase.addApplicationFont(str(font_path))
        if font_id >= 0:
            app.setFont(QFont("Arial", 10))
    load_stylesheet(app)

    screenshots_dir = project_dir / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)
    conn = create_connection(db_path)
    try:
        window = MainWindow(conn)
        window.resize(1280, 800)
        window.show()
        for page_name in ("dashboard", "eleves", "recus"):
            window.show_page(page_name)
            app.processEvents()
            output_path = screenshots_dir / f"{page_name}.png"
            if not window.grab().save(str(output_path), "PNG"):
                raise OSError(f"Impossible d'enregistrer la capture : {output_path}")
            print(f"Capture enregistrée : {output_path}")
        window.close()
    finally:
        conn.close()


if __name__ == "__main__":
    generate_screenshots()
