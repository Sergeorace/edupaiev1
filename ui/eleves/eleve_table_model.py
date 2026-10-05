"""
Modèle de table pour les élèves.
"""

from typing import Any, List, Optional

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from models.eleve import Eleve
from utils.formatters import format_montant


class EleveTableModel(QAbstractTableModel):
    """Modèle de table pour afficher les élèves."""

    def __init__(self, parent: Optional[Any] = None) -> None:
        """
        Initialise le modèle.

        Args:
            parent: Widget parent.
        """
        super().__init__(parent)
        self._eleves: List[Eleve] = []
        self._soldes: dict[int, int] = {}
        self._statuts: dict[int, str] = {}

        self._headers = [
            "ID",
            "Matricule",
            "Nom",
            "Prénom",
            "Classe",
            "Tuteur",
            "Téléphone",
            "Solde",
            "Statut",
        ]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Retourne le nombre de lignes."""
        return len(self._eleves)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Retourne le nombre de colonnes."""
        return len(self._headers)

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = ...
    ) -> Any:
        """Retourne les données d'en-tête."""
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
            and 0 <= section < len(self._headers)
        ):
            return self._headers[section]
        return None

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        """Retourne les données pour une cellule."""
        if not index.isValid():
            return None

        eleve = self._eleves[index.row()]
        column = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:
                return str(eleve.id)
            if column == 1:
                return eleve.matricule
            if column == 2:
                return eleve.nom
            if column == 3:
                return eleve.prenom
            if column == 4:
                return eleve.classe_nom or f"Classe {eleve.classe_id}"
            if column == 5:
                return eleve.tuteur
            if column == 6:
                return eleve.telephone
            if column == 7:
                solde = self._soldes.get(eleve.id, 0)
                return format_montant(solde)
            if column == 8:
                return self._statuts.get(eleve.id, "Inconnu")

        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if column == 0:
                return int(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            if column == 7:
                return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        elif role == Qt.ItemDataRole.ForegroundRole:
            if column in (7, 8):
                statut = self._statuts.get(eleve.id, "")
                if statut == "Impayé":
                    return QColor("#DC2626")
                if statut == "Partiel":
                    return QColor("#D97706")
                if statut == "Payé":
                    return QColor("#16A34A")

        return None

    def set_eleves(
        self,
        eleves: List[Eleve],
        soldes: Optional[dict[int, int]] = None,
        statuts: Optional[dict[int, str]] = None,
    ) -> None:
        """
        Définit la liste des élèves.

        Args:
            eleves: Liste des élèves.
        """
        self.beginResetModel()
        self._eleves = list(eleves)
        if soldes is not None:
            self._soldes = dict(soldes)
        if statuts is not None:
            self._statuts = dict(statuts)
        self.endResetModel()

    def set_solde(self, eleve_id: int, solde: int) -> None:
        """
        Définit le solde d'un élève.

        Args:
            eleve_id: ID de l'élève.
            solde: Solde restant.
        """
        self._soldes[eleve_id] = solde
        self._emit_row_changed(eleve_id)

    def set_statut(self, eleve_id: int, statut: str) -> None:
        """
        Définit le statut d'un élève.

        Args:
            eleve_id: ID de l'élève.
            statut: Statut (Impayé, Partiel, Payé).
        """
        self._statuts[eleve_id] = statut
        self._emit_row_changed(eleve_id)

    def _emit_row_changed(self, eleve_id: int) -> None:
        """Notifie la vue quand une donnée financière d'un élève change."""
        row = next(
            (index for index, eleve in enumerate(self._eleves) if eleve.id == eleve_id),
            None,
        )
        if row is not None:
            self.dataChanged.emit(
                self.index(row, 7),
                self.index(row, 8),
                [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ForegroundRole],
            )

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
