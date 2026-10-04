"""
Repository pour la gestion des paiements.
"""

import sqlite3
from datetime import date
from typing import List, Optional
from models.paiement import Paiement


class PaiementRepository:
    """Repository pour les opérations sur les paiements."""

    def __init__(self, conn: sqlite3.Connection):
        """
        Initialise le repository avec une connexion.

        Args:
            conn: Connexion SQLite à utiliser.
        """
        self.conn = conn

    def create(self, paiement: Paiement) -> Paiement:
        """
        Crée un nouveau paiement dans la base de données.

        Args:
            paiement: Le paiement à créer (sans l'ID).

        Returns:
            Le paiement créé avec son ID généré.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO paiements (eleve_id, annee_id, montant, date_paiement,
                                  mode_paiement, motif, statut)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                paiement.eleve_id,
                paiement.annee_id,
                paiement.montant,
                paiement.date_paiement,
                paiement.mode_paiement,
                paiement.motif,
                paiement.statut,
            ),
        )
        paiement.id = cursor.lastrowid
        return paiement

    def get_by_id(self, paiement_id: int) -> Optional[Paiement]:
        """
        Récupère un paiement par son ID.

        Args:
            paiement_id: ID du paiement.

        Returns:
            Le paiement trouvé ou None.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT p.id, p.eleve_id, p.annee_id, a.annee as annee_texte,
                   p.montant, p.date_paiement, p.mode_paiement, p.motif,
                   p.statut, p.motif_annulation, p.date_annulation,
                   e.nom as eleve_nom, e.prenom as eleve_prenom
            FROM paiements p
            LEFT JOIN annees_scolaires a ON p.annee_id = a.id
            LEFT JOIN eleves e ON p.eleve_id = e.id
            WHERE p.id = ?
            """,
            (paiement_id,),
        )
        row = cursor.fetchone()
        if row:
            return self._row_to_paiement(row)
        return None

    def get_by_eleve(
        self, eleve_id: int, annee_id: Optional[int] = None
    ) -> List[Paiement]:
        """
        Récupère tous les paiements d'un élève.

        Args:
            eleve_id: ID de l'élève.
            annee_id: Optionnel, ID de l'année scolaire pour filtrer.

        Returns:
            Liste des paiements de l'élève.
        """
        cursor = self.conn.cursor()
        if annee_id:
            cursor.execute(
                """
                SELECT p.id, p.eleve_id, p.annee_id, a.annee as annee_texte,
                       p.montant, p.date_paiement, p.mode_paiement, p.motif,
                       p.statut, p.motif_annulation, p.date_annulation,
                       e.nom as eleve_nom, e.prenom as eleve_prenom
                FROM paiements p
                LEFT JOIN annees_scolaires a ON p.annee_id = a.id
                LEFT JOIN eleves e ON p.eleve_id = e.id
                WHERE p.eleve_id = ? AND p.annee_id = ?
                ORDER BY p.date_paiement DESC
                """,
                (eleve_id, annee_id),
            )
        else:
            cursor.execute(
                """
                SELECT p.id, p.eleve_id, p.annee_id, a.annee as annee_texte,
                       p.montant, p.date_paiement, p.mode_paiement, p.motif,
                       p.statut, p.motif_annulation, p.date_annulation,
                       e.nom as eleve_nom, e.prenom as eleve_prenom
                FROM paiements p
                LEFT JOIN annees_scolaires a ON p.annee_id = a.id
                LEFT JOIN eleves e ON p.eleve_id = e.id
                WHERE p.eleve_id = ?
                ORDER BY p.date_paiement DESC
                """,
                (eleve_id,),
            )
        return [self._row_to_paiement(row) for row in cursor.fetchall()]

    def get_valid_sum(
        self, eleve_id: int, annee_id: Optional[int] = None
    ) -> int:
        """
        Calcule la somme des paiements valides d'un élève.

        Args:
            eleve_id: ID de l'élève.
            annee_id: Optionnel, ID de l'année scolaire pour filtrer.

        Returns:
            Somme des paiements valides (non annulés).
        """
        cursor = self.conn.cursor()
        if annee_id:
            cursor.execute(
                """
                SELECT COALESCE(SUM(montant), 0)
                FROM paiements
                WHERE eleve_id = ? AND annee_id = ? AND statut = 'valide'
                """,
                (eleve_id, annee_id),
            )
        else:
            cursor.execute(
                """
                SELECT COALESCE(SUM(montant), 0)
                FROM paiements
                WHERE eleve_id = ? AND statut = 'valide'
                """,
                (eleve_id,),
            )
        return cursor.fetchone()[0]

    def annuler(self, paiement_id: int, motif_annulation: str) -> None:
        """
        Annule un paiement.

        Args:
            paiement_id: ID du paiement à annuler.
            motif_annulation: Motif de l'annulation.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE paiements
            SET statut = 'annule',
                motif_annulation = ?,
                date_annulation = ?
            WHERE id = ?
            """,
            (motif_annulation, date.today(), paiement_id),
        )

    def _row_to_paiement(self, row: sqlite3.Row) -> Paiement:
        """
        Convertit une ligne de résultat en objet Paiement.

        Args:
            row: Ligne de résultat SQLite.

        Returns:
            Objet Paiement.
        """
        return Paiement(
            id=row["id"],
            eleve_id=row["eleve_id"],
            annee_id=row["annee_id"],
            annee_texte=row["annee_texte"],
            montant=row["montant"],
            date_paiement=row["date_paiement"],
            mode_paiement=row["mode_paiement"],
            motif=row["motif"],
            statut=row["statut"],
            motif_annulation=row["motif_annulation"],
            date_annulation=row["date_annulation"],
            eleve_nom=row["eleve_nom"],
            eleve_prenom=row["eleve_prenom"],
        )
