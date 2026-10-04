"""
Modèle de données pour un reçu.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Recu:
    """Représente un reçu de paiement."""

    id: int
    numero: str  # Format : "REC-2026-00001"
    paiement_id: int
    annee_id: int
    donnees_json: str  # Données figées du reçu en JSON
    date_generation: Optional[str] = None

    def get_donnees(self) -> Dict[str, Any]:
        """
        Extrait et retourne les données JSON du reçu.

        Returns:
            Dictionnaire contenant les données du reçu.
        """
        import json
        return json.loads(self.donnees_json)
