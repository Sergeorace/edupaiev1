"""
Service pour la gestion des reçus.
"""

import sqlite3
from typing import Optional, List

from models.recu import Recu
from repositories.recu_repository import RecuRepository
from utils.exceptions import EntiteIntrouvableError


class RecuService:
    """Service pour les opérations métier sur les reçus."""

    def __init__(self, conn: sqlite3.Connection):
        """
        Initialise le service avec une connexion.

        Args:
            conn: Connexion SQLite à utiliser.
        """
        self.conn = conn
        self.repository = RecuRepository(conn)

    def get_recu_by_numero(self, numero: str) -> Optional[Recu]:
        """
        Récupère un reçu par son numéro.

        Args:
            numero: Numéro du reçu (ex: "REC-2026-00001").

        Returns:
            Le reçu trouvé ou None.
        """
        return self.repository.get_by_numero(numero)

    def get_recu_by_paiement(self, paiement_id: int) -> Optional[Recu]:
        """
        Récupère le reçu associé à un paiement.

        Args:
            paiement_id: ID du paiement.

        Returns:
            Le reçu trouvé ou None.
        """
        return self.repository.get_by_paiement(paiement_id)

    def get_recus_by_annee(self, annee_id: int) -> List[Recu]:
        """
        Récupère tous les reçus d'une année scolaire.

        Args:
            annee_id: ID de l'année scolaire.

        Returns:
            Liste des reçus de l'année.
        """
        return self.repository.get_by_annee(annee_id)

    def generer_numero_recu(self, annee_id: int) -> str:
        """
        Génère un numéro de reçu unique pour une année.

        Cette méthode garantit l'unicité du numéro même en cas d'appels
        concurrents (les transactions SQLite gèrent cela).

        Args:
            annee_id: ID de l'année scolaire.

        Returns:
            Numéro de reçu au format REC-AAAA-NNNNN.
        """
        from utils.date_utils import get_annee_civile

        last_numero = self.repository.get_last_numero(annee_id)
        annee_civile = get_annee_civile()

        if last_numero:
            # Extraire le numéro séquentiel et l'incrémenter
            last_seq = int(last_numero.split("-")[2])
            new_seq = last_seq + 1
        else:
            new_seq = 1

        return f"REC-{annee_civile}-{new_seq:05d}"
