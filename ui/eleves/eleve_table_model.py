"""
Modèle de table pour les élèves.
"""

from PySide6.QtCore import QAbstractTableModel, Qt
from typing import List, Optional
from models.eleve import Eleve


class EleveTableModel(QAbstractTableModel):
    """Modèle de table pour afficher les élèves."""

    def __init__(self, parent=None):
        """
        Initialise le modèle.

        Args:
            parent: Widget parent.
        """
        super().__init__(parent)
        self._eleves: List[Eleve] = []
        self._soldes: dict = {}  # eleve_id -> solde
        self._statuts: dict = {}  # eleve_id -> statut

        self._headers = [
            "Matricule",
            "Nom",
            "Prénom",
            "Classe",
            "Tuteur",
            "Téléphone",
            "Solde",
            "Statut",
        ]

    def rowCount(self, parent=None) -> int:
        """Retourne le nombre de lignes."""
        return len(self._eleves)

    def columnCount(self, parent=None) -> int:
        """Retourne le nombre de colonnes."""
        return len(self._headers)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        """Retourne les données d'en-tête."""
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None

    def data(self, index, role: int):
        """Retourne les données pour une cellule."""
        if not index.isValid():
            return None

        eleve = self._eleves[index.row()]
        column = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:  # Matricule
                return eleve.matricule
            elif column == 1:  # Nom
                return eleve.nom
            elif column == 2:  # Prénom
                return eleve.prenom
            elif column == 3:  # Classe
                return eleve.classe_nom or f"Classe {eleve.classe_id}"
            elif column == 4:  # Tuteur
                return eleve.tuteur
            elif column == 5:  # Téléphone
                return eleve.telephone
            elif column == 6:  # Solde
                from utils.formatters import format_montant
                solde = self._soldes.get(eleve.id, 0)
                return format_montant(solde)
            elif column == 7:  # Statut
                return self._statuts.get(eleve.id, "Inconnu")

        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if column in [6]:  # Solde aligné à droite
                return Qt.AlignmentFlag.AlignRight

        elif role == Qt.ItemDataRole.ForegroundRole:
            if column == 7:  # Couleur du statut
                statut = self._statuts.get(eleve.id, "")
                if statut == "Impayé":
                    from PySide6.QtGui import QColor
                    return QColor("#e74c3c")
                elif statut == "Partiel":
                    from PySide6.QtGui import QColor
                    return QColor("#f39c12")
                elif statut == "Payé":
                    from PySide6.QtGui import QColor
                    return QColor("#27ae60")

        return None

    def set_eleves(self, eleves: List[Eleve]) -> None:
        """
        Définit la liste des élèves.

        Args:
            eleves: Liste des élèves.
        """
        self.beginResetModel()
        self._eleves = eleves
        self.endResetModel()

    def set_solde(self, eleve_id: int, solde: int) -> None:
        """
        Définit le solde d'un élève.

        Args:
            eleve_id: ID de l'élève.
            solde: Solde restant.
        """
        self._soldes[eleve_id] = solde

    def set_statut(self, eleve_id: int, statut: str) -> None:
        """
        Définit le statut d'un élève.

        Args:
            eleve_id: ID de l'élève.
            statut: Statut (Impayé, Partiel, Payé).
        """
        self._statuts[eleve_id] = statut

    def get_eleve_at(self, row: int) -> Optional[Eleve]:
        """
        Retourne l'élève à une ligne donnée.

        Args:
            row: Index de la ligne.

        Returns:
            Élève ou None.
        """
        if 0 <= row < len(self._eleves):
            return self._eleves[row]
        return None
