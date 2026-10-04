"""
Widget du tableau de bord.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtCore import Qt

from services.dashboard_service import DashboardService
from utils.formatters import format_montant


class DashboardWidget(QWidget):
    """Widget du tableau de bord."""

    def __init__(self, conn):
        """
        Initialise le widget du dashboard.

        Args:
            conn: Connexion SQLite à utiliser.
        """
        super().__init__()
        self.conn = conn
        self.service = DashboardService(conn)
        self.annee_id = 1  # Année scolaire 2025-2026

        self._setup_ui()
        self._load_data()

    def _setup_ui(self) -> None:
        """Configure l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Titre
        title = QLabel("Tableau de bord")
        title.setObjectName("title")
        layout.addWidget(title)

        # Cartes de statistiques
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        # Carte : Total encaissé
        self.card_encaisse = self._create_card("Total encaissé", "0 FCFA")
        stats_layout.addWidget(self.card_encaisse)

        # Carte : Total restant dû
        self.card_restant = self._create_card("Total restant dû", "0 FCFA")
        stats_layout.addWidget(self.card_restant)

        # Carte : Élèves impayés
        self.card_impayes = self._create_card("Élèves impayés", "0")
        stats_layout.addWidget(self.card_impayes)

        # Carte : Élèves payés
        self.card_payes = self._create_card("Élèves payés", "0")
        stats_layout.addWidget(self.card_payes)

        layout.addLayout(stats_layout)

        # Derniers paiements
        subtitle = QLabel("Derniers paiements")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        self.table_paiements = QTableWidget()
        self.table_paiements.setColumnCount(5)
        self.table_paiements.setHorizontalHeaderLabels(
            ["Élève", "Classe", "Montant", "Date", "Mode"]
        )
        self.table_paiements.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.table_paiements.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_paiements.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_paiements.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_paiements.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_paiements.setAlternatingRowColors(True)
        layout.addWidget(self.table_paiements)

    def _create_card(self, label: str, value: str) -> QFrame:
        """
        Crée une carte de statistique.

        Args:
            label: Label de la carte.
            value: Valeur initiale.

        Returns:
            Frame contenant la carte.
        """
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)

        value_label = QLabel(value)
        value_label.setObjectName("cardValue")
        card_layout.addWidget(value_label)

        label_widget = QLabel(label)
        label_widget.setObjectName("cardLabel")
        card_layout.addWidget(label_widget)

        # Stocker la référence au label de valeur
        card.value_label = value_label

        return card

    def _load_data(self) -> None:
        """Charge les données depuis le service."""
        try:
            # Statistiques
            total_encaisse = self.service.get_total_encaisse(self.annee_id)
            total_restant = self.service.get_total_restant_du(self.annee_id)
            stats = self.service.get_nombre_eleves_par_statut(self.annee_id)

            # Mettre à jour les cartes
            self.card_encaisse.value_label.setText(format_montant(total_encaisse))
            self.card_restant.value_label.setText(format_montant(total_restant))
            self.card_impayes.value_label.setText(str(stats["Impayé"]))
            self.card_payes.value_label.setText(str(stats["Payé"]))

            # Derniers paiements
            paiements = self.service.get_derniers_paiements(self.annee_id, limit=10)
            self._update_paiements_table(paiements)

        except Exception as e:
            print(f"Erreur lors du chargement des données: {e}")

    def _update_paiements_table(self, paiements: list) -> None:
        """
        Met à jour le tableau des derniers paiements.

        Args:
            paiements: Liste des paiements.
        """
        self.table_paiements.setRowCount(len(paiements))

        for row, paiement in enumerate(paiements):
            # Élève
            eleve_item = QTableWidgetItem(
                f"{paiement['eleve_nom']} {paiement['eleve_prenom']}"
            )
            self.table_paiements.setItem(row, 0, eleve_item)

            # Classe
            classe_item = QTableWidgetItem(paiement.get("classe_nom", ""))
            self.table_paiements.setItem(row, 1, classe_item)

            # Montant
            montant_item = QTableWidgetItem(format_montant(paiement["montant"]))
            montant_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table_paiements.setItem(row, 2, montant_item)

            # Date
            date_item = QTableWidgetItem(paiement["date_paiement"])
            self.table_paiements.setItem(row, 3, date_item)

            # Mode
            mode_item = QTableWidgetItem(paiement["mode_paiement"])
            self.table_paiements.setItem(row, 4, mode_item)
