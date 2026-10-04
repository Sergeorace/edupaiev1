"""
Widget de gestion des élèves.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QTableView,
    QMessageBox,
)
from PySide6.QtCore import Qt

from services.eleve_service import EleveService
from services.paiement_service import PaiementService
from ui.eleves.eleve_table_model import EleveTableModel
from ui.eleves.eleve_form import EleveFormDialog
from ui.eleves.eleve_detail import EleveDetailDialog
from ui.paiements.paiement_dialog import PaiementDialog


class ElevesWidget(QWidget):
    """Widget de gestion des élèves."""

    def __init__(self, conn):
        """
        Initialise le widget des élèves.

        Args:
            conn: Connexion SQLite à utiliser.
        """
        super().__init__()
        self.conn = conn
        self.eleve_service = EleveService(conn)
        self.paiement_service = PaiementService(conn)
        self.annee_id = 1  # Année scolaire 2025-2026

        self._setup_ui()
        self._load_eleves()

    def _setup_ui(self) -> None:
        """Configure l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Titre
        title = QPushButton("👨‍🎓 Gestion des élèves")
        title.setCheckable(False)
        title.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border: none;
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
                text-align: left;
                padding: 0;
            }
        """
        )
        layout.addWidget(title)

        # Barre de recherche et filtres
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(10)

        # Recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher (nom, prénom, matricule)...")
        self.search_input.textChanged.connect(self._on_search_changed)
        filters_layout.addWidget(self.search_input, stretch=1)

        # Filtre par statut
        self.statut_filter = QComboBox()
        self.statut_filter.addItems(["Tous", "Impayé", "Partiel", "Payé"])
        self.statut_filter.currentTextChanged.connect(self._on_filter_changed)
        filters_layout.addWidget(self.statut_filter)

        layout.addLayout(filters_layout)

        # Tableau des élèves
        self.table_model = EleveTableModel()
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectRows
        )
        self.table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.clicked.connect(self._on_table_clicked)
        layout.addWidget(self.table_view)

        # Boutons d'action
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.btn_ajouter = QPushButton("➕ Ajouter")
        self.btn_ajouter.clicked.connect(self._on_ajouter)
        buttons_layout.addWidget(self.btn_ajouter)

        self.btn_modifier = QPushButton("✏️ Modifier")
        self.btn_modifier.clicked.connect(self._on_modifier)
        self.btn_modifier.setEnabled(False)
        buttons_layout.addWidget(self.btn_modifier)

        self.btn_fiche = QPushButton("📄 Fiche")
        self.btn_fiche.clicked.connect(self._on_fiche)
        self.btn_fiche.setEnabled(False)
        buttons_layout.addWidget(self.btn_fiche)

        self.btn_payer = QPushButton("💰 Payer")
        self.btn_payer.clicked.connect(self._on_payer)
        self.btn_payer.setEnabled(False)
        buttons_layout.addWidget(self.btn_payer)

        self.btn_archiver = QPushButton("🗑️ Archiver")
        self.btn_archiver.setObjectName("dangerButton")
        self.btn_archiver.clicked.connect(self._on_archiver)
        self.btn_archiver.setEnabled(False)
        buttons_layout.addWidget(self.btn_archiver)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

    def _load_eleves(self) -> None:
        """Charge la liste des élèves."""
        try:
            eleves = self.eleve_service.list_eleves(actif_only=True)

            # Calculer solde et statut pour chaque élève
            for eleve in eleves:
                solde = self.paiement_service.calculer_solde(eleve.id, self.annee_id)
                statut = self.paiement_service.calculer_statut(eleve.id, self.annee_id)
                self.table_model.set_solde(eleve.id, solde)
                self.table_model.set_statut(eleve.id, statut)

            self.table_model.set_eleves(eleves)
            self._apply_filters()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors du chargement des élèves: {str(e)}",
            )

    def _apply_filters(self) -> None:
        """Applique les filtres de recherche et de statut."""
        search_text = self.search_input.text().lower()
        statut_filter = self.statut_filter.currentText()

        try:
            eleves = self.eleve_service.search_eleves(
                nom=search_text if search_text else None,
                prenom=search_text if search_text else None,
                matricule=search_text if search_text else None,
                actif_only=True,
            )

            # Filtrer par statut
            if statut_filter != "Tous":
                filtered = []
                for eleve in eleves:
                    statut = self.paiement_service.calculer_statut(
                        eleve.id, self.annee_id
                    )
                    if statut == statut_filter:
                        filtered.append(eleve)
                eleves = filtered

            # Recalculer solde et statut
            for eleve in eleves:
                solde = self.paiement_service.calculer_solde(eleve.id, self.annee_id)
                statut = self.paiement_service.calculer_statut(eleve.id, self.annee_id)
                self.table_model.set_solde(eleve.id, solde)
                self.table_model.set_statut(eleve.id, statut)

            self.table_model.set_eleves(eleves)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors du filtrage: {str(e)}",
            )

    def _on_search_changed(self) -> None:
        """Gère le changement de texte de recherche."""
        self._apply_filters()

    def _on_filter_changed(self) -> None:
        """Gère le changement de filtre de statut."""
        self._apply_filters()

    def _on_table_clicked(self) -> None:
        """Gère le clic sur le tableau."""
        selected = self.table_view.selectionModel().selectedRows()
        has_selection = len(selected) > 0

        self.btn_modifier.setEnabled(has_selection)
        self.btn_fiche.setEnabled(has_selection)
        self.btn_payer.setEnabled(has_selection)
        self.btn_archiver.setEnabled(has_selection)

    def _on_ajouter(self) -> None:
        """Gère l'ajout d'un élève."""
        dialog = EleveFormDialog(self.conn, self)
        if dialog.exec():
            self._load_eleves()

    def _on_modifier(self) -> None:
        """Gère la modification d'un élève."""
        selected = self.table_view.selectionModel().selectedRows()
        if not selected:
            return

        row = selected[0].row()
        eleve = self.table_model.get_eleve_at(row)
        if not eleve:
            return

        dialog = EleveFormDialog(self.conn, self, eleve)
        if dialog.exec():
            self._load_eleves()

    def _on_fiche(self) -> None:
        """Gère l'affichage de la fiche d'un élève."""
        selected = self.table_view.selectionModel().selectedRows()
        if not selected:
            return

        row = selected[0].row()
        eleve = self.table_model.get_eleve_at(row)
        if not eleve:
            return

        dialog = EleveDetailDialog(self.conn, eleve.id, self.annee_id)
        dialog.exec()

    def _on_payer(self) -> None:
        """Gère l'enregistrement d'un paiement."""
        selected = self.table_view.selectionModel().selectedRows()
        if not selected:
            return

        row = selected[0].row()
        eleve = self.table_model.get_eleve_at(row)
        if not eleve:
            return

        dialog = PaiementDialog(self.conn, eleve.id, self.annee_id)
        if dialog.exec():
            self._load_eleves()

    def _on_archiver(self) -> None:
        """Gère l'archivage d'un élève."""
        selected = self.table_view.selectionModel().selectedRows()
        if not selected:
            return

        row = selected[0].row()
        eleve = self.table_model.get_eleve_at(row)
        if not eleve:
            return

        reply = QMessageBox.question(
            self,
            "Confirmer l'archivage",
            f"Voulez-vous vraiment archiver l'élève {eleve.nom_complet} ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.eleve_service.archive_eleve(eleve.id)
                QMessageBox.information(
                    self, "Succès", "L'élève a été archivé avec succès."
                )
                self._load_eleves()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'archivage: {str(e)}")
