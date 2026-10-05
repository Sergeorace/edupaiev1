"""
Point d'entrée principal de l'application.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from types import TracebackType
from typing import Optional

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QFile, QTextStream
from PySide6.QtGui import QFontDatabase

from database.database import create_connection
from ui.main_window import MainWindow
from utils.paths import get_user_db_path, copy_db_if_needed, resource_path


def load_fonts() -> None:
    """
    Charge les polices personnalisées depuis le dossier resources/fonts.
    """
    fonts_dir = resource_path("resources/fonts")

    if isinstance(fonts_dir, str):
        fonts_path = Path(fonts_dir)
    else:
        fonts_path = fonts_dir

    if fonts_path.exists():
        # Charger Poppins
        for weight in ["SemiBold", "Bold", "ExtraBold"]:
            font_file = fonts_path / f"Poppins-{weight}.ttf"
            if font_file.exists():
                QFontDatabase.addApplicationFont(str(font_file))

        # Charger Inter
        for weight in ["Regular", "Medium", "SemiBold"]:
            font_file = fonts_path / f"Inter-{weight}.ttf"
            if font_file.exists():
                QFontDatabase.addApplicationFont(str(font_file))


def setup_logging() -> None:
    """Configure le logging vers un fichier."""
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout),
        ],
    )


def handle_exception(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: Optional[TracebackType],
) -> None:
    """
    Gestionnaire global d'exceptions.

    Journalise l'erreur et affiche un QMessageBox à l'utilisateur.
    """
    logging.error(
        "Exception non gérée",
        exc_info=(exc_type, exc_value, exc_traceback),
    )

    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    app = QApplication.instance()
    if app is not None:
        QMessageBox.critical(
            None,
            "Erreur",
            "Une erreur inattendue s'est produite. "
            "Les détails ont été enregistrés dans le journal.",
        )


def load_stylesheet(app: QApplication) -> None:
    """
    Charge le fichier de style QSS.

    Args:
        app: Instance QApplication.
    """
    style_path_str = resource_path("resources/styles/edupaie_orange.qss")
    style_path = Path(style_path_str)

    if style_path.exists():
        file = QFile(style_path_str)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            app.setStyleSheet(stream.readAll())
            file.close()


def main() -> int:
    """Point d'entrée principal."""
    # Configurer le logging
    setup_logging()

    # Installer le gestionnaire d'exceptions global
    sys.excepthook = handle_exception

    # Créer l'application
    app = QApplication(sys.argv)
    app.setApplicationName("Edupaie")
    app.setOrganizationName("Edupaie")

    # Charger les polices personnalisées
    load_fonts()

    # Charger le style
    load_stylesheet(app)

    # Initialiser la base de données utilisateur
    copy_db_if_needed()
    user_db_path = get_user_db_path()
    logging.info(f"Base de données utilisateur: {user_db_path}")

    # Créer la connexion à la base de données
    conn = create_connection(user_db_path)
    app.aboutToQuit.connect(conn.close)

    try:
        window = MainWindow(conn)
        window.show()
        return app.exec()
    except Exception:
        logging.exception("Impossible de démarrer l'application")
        QMessageBox.critical(
            None,
            "Erreur de démarrage",
            "L'application n'a pas pu démarrer. Consultez le journal pour plus "
            "d'informations.",
        )
        conn.close()
        return 1


if __name__ == "__main__":
    sys.exit(main())
