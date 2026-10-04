"""
Utilitaires pour la gestion des chemins de fichiers.
Supporte le packaging avec PyInstaller.
"""

import sys
from pathlib import Path


def resource_path(relative_path: str) -> Path:
    """
    Retourne le chemin absolu vers une ressource.

    Cette fonction gère les chemins pour le développement et pour
    l'exécutable packagé avec PyInstaller.

    Args:
        relative_path: Chemin relatif depuis la racine du projet.

    Returns:
        Chemin absolu vers la ressource.
    """
    try:
        # PyInstaller crée un dossier temporaire pour les ressources
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # En développement, utiliser le répertoire du script
        base_path = Path(__file__).parent.parent

    return base_path / relative_path


def get_user_data_dir() -> Path:
    """
    Retourne le dossier de données utilisateur de l'application.

    Ce dossier est utilisé pour stocker la base de données et les logs.
    Il est situé dans AppData sur Windows.

    Returns:
        Chemin vers le dossier de données utilisateur.
    """
    from pathlib import Path

    # Windows: %APPDATA%/GestionScolarite
    if sys.platform == "win32":
        appdata = Path.home() / "AppData" / "Roaming"
    else:
        # Linux/macOS: ~/.local/share/GestionScolarite
        appdata = Path.home() / ".local" / "share"

    data_dir = appdata / "GestionScolarite"
    data_dir.mkdir(parents=True, exist_ok=True)

    return data_dir


def get_user_db_path() -> Path:
    """
    Retourne le chemin vers la base de données utilisateur.

    Returns:
        Chemin vers school.db dans le dossier de données utilisateur.
    """
    return get_user_data_dir() / "school.db"


def copy_db_if_needed() -> None:
    """
    Copie la base de données template dans le dossier utilisateur
    si elle n'existe pas encore.
    """
    user_db_path = get_user_db_path()

    if not user_db_path.exists():
        # Copier la base de données template
        template_db_path = resource_path("school.db")

        if template_db_path.exists():
            import shutil

            shutil.copy2(template_db_path, user_db_path)
        else:
            # Si pas de template, initialiser une nouvelle base sans seed
            from database.database import init_database

            init_database(user_db_path, with_seed=False)
