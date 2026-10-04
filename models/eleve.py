"""
Modèle de données pour un élève.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Eleve:
    """Représente un élève de l'établissement."""

    id: int
    matricule: str
    nom: str
    prenom: str
    date_naissance: date
    sexe: str  # 'M' ou 'F'
    classe_id: int
    tuteur: str
    telephone: str
    classe_nom: Optional[str] = None  # Nom de la classe (jointure)
    actif: bool = True  # True = actif, False = archivé
    date_creation: Optional[str] = None

    @property
    def nom_complet(self) -> str:
        """Retourne le nom complet de l'élève."""
        return f"{self.nom} {self.prenom}"
