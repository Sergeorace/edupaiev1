"""
Module de gestion de la base de données SQLite.
Fournit la connexion, la création de la base et la gestion des transactions.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional


def get_db_path() -> Path:
    """Retourne le chemin vers le fichier de base de données."""
    return Path(__file__).parent.parent / "school.db"


def create_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Crée et retourne une connexion à la base de données.

    Args:
        db_path: Chemin vers le fichier de base de données.
                 Si None, utilise le chemin par défaut.

    Returns:
        Connexion SQLite avec les clés étrangères activées.
    """
    if db_path is None:
        db_path = get_db_path()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
    conn.execute("PRAGMA foreign_keys = ON")  # Active les clés étrangères
    return conn


@contextmanager
def get_transaction(conn: sqlite3.Connection):
    """
    Gestionnaire de contexte pour les transactions.

    Commit automatiquement si aucune exception n'est levée,
    rollback en cas d'erreur.

    Args:
        conn: Connexion SQLite à utiliser.

    Yields:
        La connexion pour exécuter des requêtes.

    Example:
        with get_transaction(conn) as cursor:
            cursor.execute("INSERT INTO ...")
            # Si aucune exception, commit automatique
    """
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def init_database(db_path: Optional[Path] = None, with_seed: bool = True) -> None:
    """
    Initialise la base de données avec le schéma et les données de test.

    Args:
        db_path: Chemin vers le fichier de base de données.
                 Si None, utilise le chemin par défaut.
        with_seed: Si True, insère les données de test. Si False, seulement le schéma.
    """
    if db_path is None:
        db_path = get_db_path()

    schema_path = Path(__file__).parent / "schema.sql"
    seed_path = Path(__file__).parent / "seed.sql"

    # Création de la base avec le schéma
    conn = create_connection(db_path)
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        conn.executescript(schema_sql)
    conn.commit()

    # Insertion des données de test
    if with_seed:
        with open(seed_path, "r", encoding="utf-8") as f:
            seed_sql = f.read()
            conn.executescript(seed_sql)
        conn.commit()

    conn.close()


if __name__ == "__main__":
    # Point d'entrée pour générer la base de données
    print("Génération de la base de données...")
    init_database()
    print(f"Base de données créée avec succès : {get_db_path()}")
