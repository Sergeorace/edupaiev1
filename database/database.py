"""
Module de gestion de la base de données SQLite.
Fournit la connexion, la création de la base et la gestion des transactions.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional


def get_db_path() -> Path:
    """Retourne le chemin vers le fichier de base de données."""
    return Path(__file__).parent.parent / "school.db"


def create_connection(
    db_path: Optional[Path | str] = None,
) -> sqlite3.Connection:
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

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
    # Active la vérification des clés étrangères sur cette connexion.
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_transaction(
    conn: sqlite3.Connection, immediate: bool = False
) -> Generator[sqlite3.Cursor, None, None]:
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
    nested = conn.in_transaction
    cursor = conn.cursor()
    if nested:
        # Utilise un savepoint pour préserver une transaction englobante.
        cursor.execute("SAVEPOINT gestion_scolarite_transaction")
    else:
        # Réserve l'écriture immédiatement si l'appelant demande un verrou exclusif.
        cursor.execute("BEGIN IMMEDIATE" if immediate else "BEGIN")
    try:
        yield cursor
        if nested:
            cursor.execute("RELEASE SAVEPOINT gestion_scolarite_transaction")
        else:
            conn.commit()
    except Exception:
        if nested:
            cursor.execute("ROLLBACK TO SAVEPOINT gestion_scolarite_transaction")
            cursor.execute("RELEASE SAVEPOINT gestion_scolarite_transaction")
        else:
            conn.rollback()
        raise


def init_database(
    db_path: Optional[Path | str] = None, with_seed: bool = True
) -> None:
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

    conn = create_connection(db_path)
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        try:
            # Crée les tables et index en une seule transaction.
            conn.executescript(f"BEGIN;\n{schema_sql}\nCOMMIT;")
        except sqlite3.Error:
            if conn.in_transaction:
                conn.rollback()
            raise

        if with_seed:
            # Vérifie si la base contient déjà des données avant d'insérer le jeu de test.
            cursor = conn.execute(
                """
                SELECT EXISTS (SELECT 1 FROM annees_scolaires)
                    OR EXISTS (SELECT 1 FROM classes)
                    OR EXISTS (SELECT 1 FROM frais_classe)
                    OR EXISTS (SELECT 1 FROM eleves)
                    OR EXISTS (SELECT 1 FROM paiements)
                    OR EXISTS (SELECT 1 FROM recus)
                """
            )
            has_data = cursor.fetchone()[0]
            if not has_data:
                with open(seed_path, "r", encoding="utf-8") as f:
                    seed_sql = f.read()
                try:
                    # Insère le jeu de test uniquement dans une base encore vide.
                    conn.executescript(f"BEGIN;\n{seed_sql}\nCOMMIT;")
                except sqlite3.Error:
                    if conn.in_transaction:
                        conn.rollback()
                    raise
    finally:
        conn.close()


if __name__ == "__main__":
    # Point d'entrée pour générer la base de données
    print("Génération de la base de données...")
    init_database()
    print(f"Base de données créée avec succès : {get_db_path()}")
