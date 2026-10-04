"""
Repository pour la gestion des reçus.
"""

import sqlite3
from typing import List, Optional
from models.recu import Recu


class RecuRepository:
    """Repository pour les opérations sur les reçus."""

    def __init__(self, conn: sqlite3.Connection):
        """
        Initialise le repository avec une connexion.

        Args:
            conn: Connexion SQLite à utiliser.
        """
        self.conn = conn

    def create(self, recu: Recu) -> Recu:
        """
        Crée un nouveau reçu dans la base de données.

        Args:
            recu: Le reçu à créer (sans l'ID).

        Returns:
            Le reçu créé avec son ID généré.
        """
        cursor = self.conn.cursor()
        # Enregistre les données figées du reçu, sans gérer la transaction.
        cursor.execute(
            """
            INSERT INTO recus (numero, paiement_id, annee_id, donnees_json)
            VALUES (?, ?, ?, ?)
            """,
            (recu.numero, recu.paiement_id, recu.annee_id, recu.donnees_json),
        )
        recu.id = cursor.lastrowid
        return recu

    def get_by_id(self, recu_id: int) -> Optional[Recu]:
        """
        Récupère un reçu par son ID.

        Args:
            recu_id: ID du reçu.

        Returns:
            Le reçu trouvé ou None.
        """
        cursor = self.conn.cursor()
        # Recherche un reçu à partir de son identifiant interne.
        cursor.execute(
            """
            SELECT id, numero, paiement_id, annee_id, donnees_json, date_generation
            FROM recus
            WHERE id = ?
            """,
            (recu_id,),
        )
        row = cursor.fetchone()
        if row:
            return self._row_to_recu(row)
        return None

    def get_by_numero(self, numero: str) -> Optional[Recu]:
        """
        Récupère un reçu par son numéro.

        Args:
            numero: Numéro du reçu (ex: "REC-2026-00001").

        Returns:
            Le reçu trouvé ou None.
        """
        cursor = self.conn.cursor()
        # Recherche un reçu à partir de son numéro unique.
        cursor.execute(
            """
            SELECT id, numero, paiement_id, annee_id, donnees_json, date_generation
            FROM recus
            WHERE numero = ?
            """,
            (numero,),
        )
        row = cursor.fetchone()
        if row:
            return self._row_to_recu(row)
        return None

    def get_by_paiement(self, paiement_id: int) -> Optional[Recu]:
        """
        Récupère le reçu associé à un paiement.

        Args:
            paiement_id: ID du paiement.

        Returns:
            Le reçu trouvé ou None.
        """
        cursor = self.conn.cursor()
        # Recherche le reçu associé à un paiement.
        cursor.execute(
            """
            SELECT id, numero, paiement_id, annee_id, donnees_json, date_generation
            FROM recus
            WHERE paiement_id = ?
            """,
            (paiement_id,),
        )
        row = cursor.fetchone()
        if row:
            return self._row_to_recu(row)
        return None

    def get_by_annee(self, annee_id: int) -> List[Recu]:
        """
        Récupère tous les reçus d'une année scolaire.

        Args:
            annee_id: ID de l'année scolaire.

        Returns:
            Liste des reçus de l'année.
        """
        cursor = self.conn.cursor()
        # Liste les reçus d'une année dans l'ordre de leur numéro.
        cursor.execute(
            """
            SELECT id, numero, paiement_id, annee_id, donnees_json, date_generation
            FROM recus
            WHERE annee_id = ?
            ORDER BY numero
            """,
            (annee_id,),
        )
        return [self._row_to_recu(row) for row in cursor.fetchall()]

    def get_last_numero(self, annee_id: int) -> Optional[str]:
        """
        Récupère le dernier numéro de reçu pour une année scolaire.

        Args:
            annee_id: ID de l'année scolaire.

        Returns:
            Le dernier numéro de reçu ou None si aucun reçu pour cette année.
        """
        cursor = self.conn.cursor()
        # Récupère le dernier numéro attribué pour une année donnée.
        cursor.execute(
            """
            SELECT numero
            FROM recus
            WHERE annee_id = ?
            ORDER BY numero DESC
            LIMIT 1
            """,
            (annee_id,),
        )
        row = cursor.fetchone()
        if row:
            return row["numero"]
        return None

    def _row_to_recu(self, row: sqlite3.Row) -> Recu:
        """
        Convertit une ligne de résultat en objet Recu.

        Args:
            row: Ligne de résultat SQLite.

        Returns:
            Objet Recu.
        """
        return Recu(
            id=row["id"],
            numero=row["numero"],
            paiement_id=row["paiement_id"],
            annee_id=row["annee_id"],
            donnees_json=row["donnees_json"],
            date_generation=row["date_generation"],
        )
