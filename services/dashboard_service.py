"""
Service pour le dashboard et les statistiques.
"""

import sqlite3
from typing import Dict, List

from repositories.dashboard_repository import DashboardRepository


class DashboardService:
    """Service pour les statistiques du dashboard."""

    def __init__(self, conn: sqlite3.Connection):
        """
        Initialise le service avec une connexion.

        Args:
            conn: Connexion SQLite à utiliser.
        """
        self.conn = conn
        self.repository = DashboardRepository(conn)

    def get_total_encaisse(self, annee_id: int) -> int:
        """
        Récupère le total encaissé pour une année scolaire.

        Args:
            annee_id: ID de l'année scolaire.

        Returns:
            Somme des paiements valides en FCFA.
        """
        return self.repository.get_total_encaisse(annee_id)

    def get_total_restant_du(self, annee_id: int) -> int:
        """
        Récupère le total restant dû pour une année scolaire.

        Args:
            annee_id: ID de l'année scolaire.

        Returns:
            Somme des soldes restants en FCFA.
        """
        return self.repository.get_total_restant_du(annee_id)

    def get_nombre_eleves_par_statut(self, annee_id: int) -> Dict[str, int]:
        """
        Récupère le nombre d'élèves par statut de paiement.

        Args:
            annee_id: ID de l'année scolaire.

        Returns:
            Dictionnaire avec les compteurs : {"Impayé": X, "Partiel": Y, "Payé": Z}.
        """
        return self.repository.get_nombre_eleves_par_statut(annee_id)

    def get_derniers_paiements(self, annee_id: int, limit: int = 10) -> List[Dict]:
        """
        Récupère les derniers paiements enregistrés.

        Args:
            annee_id: ID de l'année scolaire.
            limit: Nombre maximum de paiements à retourner.

        Returns:
            Liste des paiements avec détails.
        """
        return self.repository.get_derniers_paiements(annee_id, limit)
