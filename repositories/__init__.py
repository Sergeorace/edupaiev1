"""Package repositories."""

from repositories.eleve_repository import EleveRepository
from repositories.paiement_repository import PaiementRepository
from repositories.recu_repository import RecuRepository
from repositories.frais_classe_repository import FraisClasseRepository
from repositories.dashboard_repository import DashboardRepository

__all__ = [
    "EleveRepository",
    "PaiementRepository",
    "RecuRepository",
    "FraisClasseRepository",
    "DashboardRepository",
]
