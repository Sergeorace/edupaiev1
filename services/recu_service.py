"""
Service pour la gestion des reçus.
"""

import sqlite3
from typing import Optional, List

from models.recu import Recu
from repositories.recu_repository import RecuRepository
from utils.date_utils import extract_annee_from_recu_numero, get_annee_civile
from utils.exceptions import RegleMetierError


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

        Note:
            Cette méthode doit être appelée dans la transaction qui crée le
            paiement et le reçu afin que deux enregistrements concurrents ne
            reçoivent pas le même numéro.
        """
        annee_civile = get_annee_civile()
        last_sequence = 0
        for recu in self.repository.get_by_annee(annee_id):
            try:
                annee_recu = extract_annee_from_recu_numero(recu.numero)
            except ValueError as error:
                raise RegleMetierError(
                    "Un numéro de reçu enregistré est invalide."
                ) from error
            if annee_recu == annee_civile:
                last_sequence = max(
                    last_sequence, int(recu.numero.split("-")[2])
                )

        if last_sequence >= 99999:
            raise RegleMetierError(
                "La séquence de numéros de reçu est épuisée pour cette année."
            )

        return f"REC-{annee_civile}-{last_sequence + 1:05d}"
