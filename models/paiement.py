"""
Modèle de données pour un paiement.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Paiement:
    """Représente un paiement effectué par un élève."""

    id: int
    eleve_id: int
    annee_id: int
    montant: int
    date_paiement: date
    mode_paiement: str  # "Espèces", "Chèque", "Virement", "Mobile"
    annee_texte: Optional[str] = None  # Texte de l'année (jointure)
    motif: Optional[str] = None
    statut: str = "valide"  # "valide" ou "annule"
    motif_annulation: Optional[str] = None
    date_annulation: Optional[date] = None
    eleve_nom: Optional[str] = None  # Nom de l'élève (jointure)
    eleve_prenom: Optional[str] = None  # Prénom de l'élève (jointure)
