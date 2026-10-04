"""Écran de synthèse des encaissements et des élèves."""

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from services.dashboard_service import DashboardService
from ui.error_handling import run_service_operation
from utils.date_utils import parse_date
from utils.formatters import format_date, format_montant


class DashboardWidget(QWidget):
    """Affiche les principaux indicateurs d'une année scolaire."""

    def __init__(self, conn: Any, annee_id: int = 1) -> None:
        """Initialise le tableau de bord et charge ses données."""
        super().__init__()
        self.service = DashboardService(conn)
        self.annee_id = annee_id
        self._setup_ui()
        self._load_data()

    def _setup_ui(self) -> None:
        """Construit les indicateurs et le tableau des paiements récents."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(22)

        title = QLabel("Tableau de bord")
        title.setObjectName("title")
        layout.addWidget(title)

        cards_layout = QGridLayout()
        cards_layout.setHorizontalSpacing(14)
        cards_layout.setVerticalSpacing(14)
        self.card_encaisse = self._create_card("Total encaissé", "0 FCFA")
        self.card_restant = self._create_card("Total restant dû", "0 FCFA")
        self.card_impayes = self._create_card("Élèves impayés", "0")
        self.card_partiels = self._create_card("Élèves partiellement payés", "0")
        self.card_payes = self._create_card("Élèves payés", "0")
        cards = (
            self.card_encaisse,
            self.card_restant,
            self.card_impayes,
            self.card_partiels,
            self.card_payes,
        )
        for index, card in enumerate(cards):
            cards_layout.addWidget(card, index // 3, index % 3)
        layout.addLayout(cards_layout)

        subtitle = QLabel("Derniers paiements")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        self.table_paiements = QTableWidget()
        self.table_paiements.setObjectName("recentPaymentsTable")
        self.table_paiements.setColumnCount(6)
        self.table_paiements.setHorizontalHeaderLabels(
            ["Élève", "Classe", "Montant", "Date", "Mode", "Statut"]
        )
        self.table_paiements.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        for column in range(1, 6):
            self.table_paiements.horizontalHeader().setSectionResizeMode(
                column, QHeaderView.ResizeMode.ResizeToContents
            )
        self.table_paiements.setAlternatingRowColors(True)
        self.table_paiements.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table_paiements.verticalHeader().setVisible(False)
        layout.addWidget(self.table_paiements, stretch=1)

    def _create_card(self, label: str, value: str) -> QFrame:
        """Construit une carte pour un indicateur."""
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        value_label = QLabel(value)
        value_label.setObjectName("cardValue")
        card_layout.addWidget(value_label)
        label_widget = QLabel(label)
        label_widget.setObjectName("cardLabel")
        card_layout.addWidget(label_widget)
        card.value_label = value_label
        return card

    def _get_dashboard_data(self) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Récupère les indicateurs et les derniers paiements via le service."""
        stats = {
            "encaisse": self.service.get_total_encaisse(self.annee_id),
            "restant": self.service.get_total_restant_du(self.annee_id),
            "statuts": self.service.get_nombre_eleves_par_statut(self.annee_id),
        }
        paiements = self.service.get_derniers_paiements(self.annee_id, limit=10)
        return stats, paiements

    def _load_data(self) -> None:
        """Met à jour l'affichage à partir des services."""
        success, result = run_service_operation(
            self, "le chargement du tableau de bord", self._get_dashboard_data
        )
        if not success or result is None:
            return
        stats, paiements = result
        self.card_encaisse.value_label.setText(format_montant(stats["encaisse"]))
        self.card_restant.value_label.setText(format_montant(stats["restant"]))
        self.card_impayes.value_label.setText(str(stats["statuts"]["Impayé"]))
        self.card_partiels.value_label.setText(str(stats["statuts"]["Partiel"]))
        self.card_payes.value_label.setText(str(stats["statuts"]["Payé"]))
        self._update_paiements_table(paiements)

    def _update_paiements_table(self, paiements: list[dict[str, Any]]) -> None:
        """Affiche les lignes des paiements les plus récents."""
        self.table_paiements.setRowCount(len(paiements))
        for row, paiement in enumerate(paiements):
            values = (
                f"{paiement['eleve_nom']} {paiement['eleve_prenom']}",
                paiement.get("classe_nom") or "—",
                format_montant(paiement["montant"]),
                format_date(parse_date(paiement["date_paiement"])),
                paiement["mode_paiement"],
                "Annulé" if paiement["statut"] == "annule" else "Valide",
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 2:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                if column == 5 and paiement["statut"] == "annule":
                    item.setForeground(Qt.GlobalColor.red)
                self.table_paiements.setItem(row, column, item)
