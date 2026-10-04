"""
Fiche détaillée d'un élève.
"""

from typing import Any, Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QMessageBox,
    QHeaderView,
    QWidget,
)
from PySide6.QtCore import Qt

from services.eleve_service import EleveService
from services.paiement_service import PaiementService
from services.recu_service import RecuService
from utils.formatters import format_montant, format_date
from ui.recus.recu_viewer import open_recu_direct
from ui.error_handling import run_service_operation
from models.eleve import Eleve
from models.paiement import Paiement
from models.recu import Recu
from utils.date_utils import parse_date


class EleveDetailDialog(QDialog):
    """Dialogue de fiche d'élève."""

    def __init__(
        self,
        conn: Any,
        eleve_id: int,
        annee_id: int,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Initialise le dialogue.

        Args:
            conn: Connexion SQLite.
            eleve_id: ID de l'élève.
            annee_id: ID de l'année scolaire.
        """
        super().__init__(parent)
        self.conn = conn
        self.eleve_service = EleveService(conn)
        self.paiement_service = PaiementService(conn)
        self.recu_service = RecuService(conn)
        self.eleve_id = eleve_id
        self.annee_id = annee_id

        self.setWindowTitle("Fiche élève")
        self.setMinimumSize(700, 600)

        self.paiement_ids: list[int] = []

        self._setup_ui()
        self._load_data()

    def _setup_ui(self) -> None:
        """Configure l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Informations de l'élève
        self.info_label = QLabel()
        self.info_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.info_label)

        # Statistiques financières
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        self.lbl_frais_dus = QLabel()
        self.lbl_frais_dus.setStyleSheet("font-size: 14px;")
        stats_layout.addWidget(self.lbl_frais_dus)

        self.lbl_total_paye = QLabel()
        self.lbl_total_paye.setStyleSheet("font-size: 14px;")
        stats_layout.addWidget(self.lbl_total_paye)

        self.lbl_solde = QLabel()
        self.lbl_solde.setStyleSheet("font-size: 14px; font-weight: bold;")
        stats_layout.addWidget(self.lbl_solde)

        self.lbl_statut = QLabel()
        self.lbl_statut.setStyleSheet("font-size: 14px; font-weight: bold;")
        stats_layout.addWidget(self.lbl_statut)

        layout.addLayout(stats_layout)

        # Historique des paiements
        subtitle = QLabel("Historique des paiements")
        subtitle.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(subtitle)

        self.table_paiements = QTableWidget()
        self.table_paiements.setColumnCount(6)
        self.table_paiements.setHorizontalHeaderLabels(
            ["Date", "Montant", "Mode", "Motif", "Statut", "Reçu"]
        )
        self.table_paiements.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_paiements.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_paiements.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_paiements.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.Stretch
        )
        self.table_paiements.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_paiements.horizontalHeader().setSectionResizeMode(
            5, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_paiements.setAlternatingRowColors(True)
        layout.addWidget(self.table_paiements)

        # Boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.btn_annuler = QPushButton("Annuler paiement")
        self.btn_annuler.setObjectName("dangerButton")
        self.btn_annuler.clicked.connect(self._on_annuler_paiement)
        self.btn_annuler.setEnabled(False)
        buttons_layout.addWidget(self.btn_annuler)

        self.btn_fermer = QPushButton("Fermer")
        self.btn_fermer.clicked.connect(self.accept)
        buttons_layout.addWidget(self.btn_fermer)

        layout.addLayout(buttons_layout)

        # Connecter la sélection et le double-clic
        self.table_paiements.itemSelectionChanged.connect(self._on_selection_changed)
        self.table_paiements.cellDoubleClicked.connect(self._on_cell_double_clicked)

    def _load_data(self) -> None:
        """Charge les données de l'élève."""
        success, result = run_service_operation(
            self, "le chargement de la fiche élève", self._get_data
        )
        if not success or result is None:
            return

        eleve, frais_dus, total_paye, solde, statut, paiements, recus = result
        if eleve is None:
            QMessageBox.warning(self, "Élève introuvable", "Cet élève n'existe plus.")
            self.reject()
            return

        self.info_label.setText(
            f"{eleve.nom_complet} · {eleve.classe_nom or 'Classe inconnue'}"
        )
        self.lbl_frais_dus.setText(f"Frais dus : {format_montant(frais_dus)}")
        self.lbl_total_paye.setText(f"Total payé : {format_montant(total_paye)}")
        self.lbl_solde.setText(f"Solde : {format_montant(solde)}")
        self.lbl_statut.setText(f"Statut : {statut}")
        status_colors = {
            "Impayé": "#e74c3c",
            "Partiel": "#d97706",
            "Payé": "#16804a",
        }
        self.lbl_statut.setStyleSheet(
            f"font-size: 14px; font-weight: bold; "
            f"color: {status_colors.get(statut, '#2c3e50')};"
        )
        self._update_paiements_table(paiements, recus)

    def _get_data(
        self,
    ) -> tuple[
        Optional[Eleve],
        int,
        int,
        int,
        str,
        list[Paiement],
        dict[int, Optional[Recu]],
    ]:
        """Récupère les données de la fiche uniquement par les services."""
        eleve = self.eleve_service.get_eleve_by_id(self.eleve_id)
        if eleve is None:
            return None, 0, 0, 0, "", [], {}
        paiements = self.paiement_service.get_paiements_eleve(
            self.eleve_id, self.annee_id
        )
        recus = {
            paiement.id: self.recu_service.get_recu_by_paiement(paiement.id)
            for paiement in paiements
        }
        return (
            eleve,
            self.paiement_service.calculer_frais_dus(self.eleve_id, self.annee_id),
            self.paiement_service.calculer_total_paye(self.eleve_id, self.annee_id),
            self.paiement_service.calculer_solde(self.eleve_id, self.annee_id),
            self.paiement_service.calculer_statut(self.eleve_id, self.annee_id),
            paiements,
            recus,
        )

    def _update_paiements_table(
        self, paiements: list[Paiement], recus: dict[int, Optional[Recu]]
    ) -> None:
        """
        Met à jour le tableau des paiements.

        Args:
            paiements: Liste des paiements.
        """
        self.table_paiements.setRowCount(len(paiements))
        self.paiement_ids = []  # Stocker les IDs pour l'annulation

        for row, paiement in enumerate(paiements):
            self.paiement_ids.append(paiement.id)

            # Date
            date_paiement = paiement.date_paiement
            if isinstance(date_paiement, str):
                date_paiement = parse_date(date_paiement)
            date_item = QTableWidgetItem(format_date(date_paiement))
            self.table_paiements.setItem(row, 0, date_item)

            # Montant
            montant_item = QTableWidgetItem(format_montant(paiement.montant))
            montant_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table_paiements.setItem(row, 1, montant_item)

            # Mode
            mode_item = QTableWidgetItem(paiement.mode_paiement)
            self.table_paiements.setItem(row, 2, mode_item)

            # Motif
            motif_item = QTableWidgetItem(paiement.motif or "-")
            self.table_paiements.setItem(row, 3, motif_item)

            # Statut
            libelle_statut = "Annulé" if paiement.statut == "annule" else "Valide"
            statut_item = QTableWidgetItem(libelle_statut)
            if paiement.statut == "annule":
                statut_item.setForeground(Qt.GlobalColor.red)
            self.table_paiements.setItem(row, 4, statut_item)

            # Reçu
            recu = recus.get(paiement.id)
            if recu:
                recu_item = QTableWidgetItem(recu.numero)
                recu_item.setForeground(Qt.GlobalColor.blue)
                self.table_paiements.setItem(row, 5, recu_item)
            else:
                recu_item = QTableWidgetItem("-")
                self.table_paiements.setItem(row, 5, recu_item)

    def _on_selection_changed(self) -> None:
        """Gère le changement de sélection dans le tableau."""
        selected = self.table_paiements.selectionModel().selectedRows()
        has_selection = len(selected) > 0

        if has_selection:
            row = selected[0].row()
            statut_item = self.table_paiements.item(row, 4)
            if statut_item and statut_item.text() == "Valide":
                self.btn_annuler.setEnabled(True)
            else:
                self.btn_annuler.setEnabled(False)
        else:
            self.btn_annuler.setEnabled(False)

    def _on_cell_double_clicked(self, row: int, column: int) -> None:
        """
        Gère le double-clic sur une cellule.
        Ouvre le reçu si on clique sur la colonne Reçu.

        Args:
            row: Ligne cliquée.
            column: Colonne cliquée.
        """
        if column == 5:  # Colonne Reçu
            if row < 0 or row >= len(self.paiement_ids):
                return

            paiement_id = self.paiement_ids[row]
            open_recu_direct(self.conn, paiement_id, self)

    def _on_annuler_paiement(self) -> None:
        """Gère l'annulation d'un paiement."""
        selected = self.table_paiements.selectionModel().selectedRows()
        if not selected:
            return

        row = selected[0].row()
        if row < 0 or row >= len(self.paiement_ids):
            return

        paiement_id = self.paiement_ids[row]

        # Pour simplifier, on demande juste le motif
        from PySide6.QtWidgets import QInputDialog

        motif, ok = QInputDialog.getText(
            self, "Motif d'annulation", "Motif de l'annulation:"
        )

        if ok and motif.strip():
            success, _ = run_service_operation(
                self,
                "l'annulation du paiement",
                lambda: self.paiement_service.annuler_paiement(
                    paiement_id, motif.strip()
                ),
            )
            if success:
                QMessageBox.information(self, "Succès", "Le paiement a été annulé.")
                self._load_data()
