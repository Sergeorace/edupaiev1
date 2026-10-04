"""
Point d'entrée principal de l'application.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QFile, QTextStream

from database.database import create_connection
from ui.main_window import MainWindow
from utils.paths import get_user_db_path, copy_db_if_needed


def setup_logging():
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


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Gestionnaire global d'exceptions.

    Journalise l'erreur et affiche un QMessageBox à l'utilisateur.
    """
    logging.error(
        "Exception non gérée",
        exc_info=(exc_type, exc_value, exc_traceback),
    )

    # Afficher un message d'erreur à l'utilisateur
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle("Erreur")
    msg.setText("Une erreur inattendue s'est produite.")
    msg.setInformativeText(
        "L'application va continuer de fonctionner. "
        "Si le problème persiste, veuillez contacter le support technique."
    )
    msg.setDetailedText(f"{exc_type.__name__}: {str(exc_value)}")
    msg.exec()


def load_stylesheet(app: QApplication) -> None:
    """
    Charge le fichier de style QSS.

    Args:
        app: Instance QApplication.
    """
    style_path = Path(__file__).parent / "resources" / "styles" / "style.qss"
    if style_path.exists():
        file = QFile(str(style_path))
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            app.setStyleSheet(stream.readAll())
            file.close()


def main():
    """Point d'entrée principal."""
    # Configurer le logging
    setup_logging()

    # Installer le gestionnaire d'exceptions global
    sys.excepthook = handle_exception

    # Créer l'application
    app = QApplication(sys.argv)
    app.setApplicationName("Gestion Scolarité")
    app.setOrganizationName("Ecole")

    # Charger le style
    load_stylesheet(app)

    # Initialiser la base de données utilisateur
    copy_db_if_needed()
    user_db_path = get_user_db_path()
    logging.info(f"Base de données utilisateur: {user_db_path}")

    # Créer la connexion à la base de données
    conn = create_connection(user_db_path)

    # Créer et afficher la fenêtre principale
    window = MainWindow(conn)
    window.show()

    # Exécuter l'application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
