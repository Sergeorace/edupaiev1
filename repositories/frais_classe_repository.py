"""
Repository pour la gestion des frais de classe.
"""

import sqlite3
from typing import List, Optional, Dict


class FraisClasseRepository:
    """Repository pour les opérations sur les frais de classe."""

    def __init__(self, conn: sqlite3.Connection):
        """
        Initialise le repository avec une connexion.

        Args:
            conn: Connexion SQLite à utiliser.
        """
        self.conn = conn

    def get_by_classe_and_annee(self, classe_id: int, annee_id: int) -> List[Dict]:
        """
        Récupère la grille de frais d'une classe pour une année.

        Args:
            classe_id: ID de la classe.
            annee_id: ID de l'année scolaire.

        Returns:
            Liste des frais avec type_frais et montant.
        """
        cursor = self.conn.cursor()
        # Récupère la grille tarifaire d'une classe pour une année scolaire.
        cursor.execute(
            """
            SELECT type_frais, montant, description
            FROM frais_classe
            WHERE classe_id = ? AND annee_id = ?
            ORDER BY type_frais
            """,
            (classe_id, annee_id),
        )
        return [
            {
                "type_frais": row["type_frais"],
                "montant": row["montant"],
                "description": row["description"],
            }
            for row in cursor.fetchall()
        ]

    def get_total_by_classe_and_annee(self, classe_id: int, annee_id: int) -> int:
        """
        Calcule le total des frais d'une classe pour une année.

        Args:
            classe_id: ID de la classe.
            annee_id: ID de l'année scolaire.

        Returns:
            Somme des frais.
        """
        cursor = self.conn.cursor()
        # Additionne les lignes de frais de la classe pour l'année demandée.
        cursor.execute(
            """
            SELECT COALESCE(SUM(montant), 0)
            FROM frais_classe
            WHERE classe_id = ? AND annee_id = ?
            """,
            (classe_id, annee_id),
        )
        return cursor.fetchone()[0]
