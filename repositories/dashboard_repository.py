"""
Repository pour les requêtes d'agrégation du dashboard.
"""

import sqlite3
from typing import Dict, List


class DashboardRepository:
    """Repository pour les statistiques du dashboard."""

    def __init__(self, conn: sqlite3.Connection):
        """
        Initialise le repository avec une connexion.

        Args:
            conn: Connexion SQLite à utiliser.
        """
        self.conn = conn

    def get_total_encaisse(self, annee_id: int) -> int:
        """
        Calcule le total encaissé pour une année scolaire.

        Args:
            annee_id: ID de l'année scolaire.

        Returns:
            Somme des paiements valides.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT COALESCE(SUM(montant), 0)
            FROM paiements
            WHERE annee_id = ? AND statut = 'valide'
            """,
            (annee_id,),
        )
        return cursor.fetchone()[0]

    def get_total_restant_du(self, annee_id: int) -> int:
        """
        Calcule le total restant dû pour une année scolaire.

        Args:
            annee_id: ID de l'année scolaire.

        Returns:
            Somme des soldes restants de tous les élèves.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT COALESCE(SUM(frais_dus - total_paye), 0)
            FROM (
                SELECT
                    e.id as eleve_id,
                    (SELECT COALESCE(SUM(fc.montant), 0)
                     FROM frais_classe fc
                     WHERE fc.classe_id = e.classe_id AND fc.annee_id = ?) as frais_dus,
                    (SELECT COALESCE(SUM(p.montant), 0)
                     FROM paiements p
                     WHERE p.eleve_id = e.id AND p.annee_id = ? AND p.statut = 'valide') as total_paye
                FROM eleves e
                WHERE e.actif = 1
            )
            """,
            (annee_id, annee_id),
        )
        return cursor.fetchone()[0]

    def get_nombre_eleves_par_statut(self, annee_id: int) -> Dict[str, int]:
        """
        Compte le nombre d'élèves par statut de paiement.

        Args:
            annee_id: ID de l'année scolaire.

        Returns:
            Dictionnaire avec les compteurs : {"Impayé": X, "Partiel": Y, "Payé": Z}.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT
                CASE
                    WHEN total_paye = 0 THEN 'Impayé'
                    WHEN solde = 0 THEN 'Payé'
                    ELSE 'Partiel'
                END as statut,
                COUNT(*) as nombre
            FROM (
                SELECT
                    e.id,
                    (SELECT COALESCE(SUM(p.montant), 0)
                     FROM paiements p
                     WHERE p.eleve_id = e.id AND p.annee_id = ? AND p.statut = 'valide') as total_paye,
                    (SELECT COALESCE(SUM(fc.montant), 0)
                     FROM frais_classe fc
                     WHERE fc.classe_id = e.classe_id AND fc.annee_id = ?) -
                    (SELECT COALESCE(SUM(p.montant), 0)
                     FROM paiements p
                     WHERE p.eleve_id = e.id AND p.annee_id = ? AND p.statut = 'valide') as solde
                FROM eleves e
                WHERE e.actif = 1
            )
            GROUP BY statut
            """,
            (annee_id, annee_id, annee_id),
        )

        result = {"Impayé": 0, "Partiel": 0, "Payé": 0}
        for row in cursor.fetchall():
            result[row["statut"]] = row["nombre"]

        return result

    def get_derniers_paiements(self, annee_id: int, limit: int = 10) -> List[Dict]:
        """
        Récupère les derniers paiements enregistrés.

        Args:
            annee_id: ID de l'année scolaire.
            limit: Nombre maximum de paiements à retourner.

        Returns:
            Liste des paiements avec détails.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT
                p.id,
                p.montant,
                p.date_paiement,
                p.mode_paiement,
                p.statut,
                e.nom as eleve_nom,
                e.prenom as eleve_prenom,
                c.nom as classe_nom
            FROM paiements p
            LEFT JOIN eleves e ON p.eleve_id = e.id
            LEFT JOIN classes c ON e.classe_id = c.id
            WHERE p.annee_id = ?
            ORDER BY p.date_paiement DESC, p.id DESC
            LIMIT ?
            """,
            (annee_id, limit),
        )

        return [
            {
                "id": row["id"],
                "montant": row["montant"],
                "date_paiement": row["date_paiement"],
                "mode_paiement": row["mode_paiement"],
                "statut": row["statut"],
                "eleve_nom": row["eleve_nom"],
                "eleve_prenom": row["eleve_prenom"],
                "classe_nom": row["classe_nom"],
            }
            for row in cursor.fetchall()
        ]
