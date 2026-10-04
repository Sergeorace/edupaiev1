"""Écran de recherche et de gestion des élèves."""

from typing import Any, Optional

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from services.eleve_service import EleveService
from services.paiement_service import PaiementService
from ui.eleves.eleve_detail import EleveDetailDialog
from ui.eleves.eleve_form import EleveFormDialog
from ui.eleves.eleve_table_model import EleveTableModel
from ui.error_handling import run_service_operation
from ui.paiements.paiement_dialog import PaiementDialog
from models.eleve import Eleve


class ElevesWidget(QWidget):
    """Widget de gestion des élèves actifs."""

    def __init__(self, conn: Any, annee_id: int = 1) -> None:
        """Initialise l'écran des élèves avec les services requis."""
        super().__init__()
        self.conn = conn
        self.eleve_service = EleveService(conn)
        self.paiement_service = PaiementService(conn)
        self.annee_id = annee_id
        self._eleves_actifs: list[Eleve] = []
        self._soldes: dict[int, int] = {}
        self._statuts: dict[int, str] = {}

        self._setup_ui()
        self._load_eleves()

    def _setup_ui(self) -> None:
        """Construit les contrôles de recherche, le tableau et les actions."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        title = QLabel("Gestion des élèves")
        title.setObjectName("title")
        layout.addWidget(title)

        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(10)
        self.search_input = QLineEdit()
        self.search_input.setObjectName("studentSearch")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setPlaceholderText(
            "Rechercher par nom, prénom ou matricule"
        )
        self.search_input.textChanged.connect(self._apply_filters)
        filters_layout.addWidget(self.search_input, stretch=1)

        self.classe_filter = QComboBox()
        self.classe_filter.setObjectName("classFilter")
        self.classe_filter.addItem("Toutes les classes", None)
        self.classe_filter.currentIndexChanged.connect(self._apply_filters)
        filters_layout.addWidget(self.classe_filter)

        self.statut_filter = QComboBox()
        self.statut_filter.setObjectName("statusFilter")
        self.statut_filter.addItems(["Tous les statuts", "Impayé", "Partiel", "Payé"])
        self.statut_filter.currentIndexChanged.connect(self._apply_filters)
        filters_layout.addWidget(self.statut_filter)
        layout.addLayout(filters_layout)

        self.table_model = EleveTableModel(self)
        self.table_view = QTableView()
        self.table_view.setObjectName("studentsTable")
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSortingEnabled(False)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.setMinimumHeight(400)
        self.table_view.selectionModel().selectionChanged.connect(
            self._on_selection_changed
        )
        self.table_view.doubleClicked.connect(self._on_fiche)
        layout.addWidget(self.table_view, stretch=1)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        self.btn_ajouter = QPushButton("Ajouter")
        self.btn_ajouter.setObjectName("successButton")
        self.btn_ajouter.clicked.connect(self._on_ajouter)
        buttons_layout.addWidget(self.btn_ajouter)

        self.btn_modifier = QPushButton("Modifier")
        self.btn_modifier.clicked.connect(self._on_modifier)
        buttons_layout.addWidget(self.btn_modifier)

        self.btn_fiche = QPushButton("Fiche")
        self.btn_fiche.clicked.connect(self._on_fiche)
        buttons_layout.addWidget(self.btn_fiche)

        self.btn_payer = QPushButton("Payer")
        self.btn_payer.clicked.connect(self._on_payer)
        buttons_layout.addWidget(self.btn_payer)

        self.btn_archiver = QPushButton("Archiver")
        self.btn_archiver.setObjectName("dangerButton")
        self.btn_archiver.clicked.connect(self._on_archiver)
        buttons_layout.addWidget(self.btn_archiver)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        self._set_action_buttons_enabled(False)

    def _load_eleves(self) -> None:
        """Charge les élèves et leurs statistiques financières depuis les services."""
        success, result = run_service_operation(
            self, "le chargement des élèves", self._get_eleves_and_finances
        )
        if not success or result is None:
            return

        eleves, soldes, statuts = result
        self._eleves_actifs = eleves
        self._soldes = soldes
        self._statuts = statuts

        selected_class = self.classe_filter.currentData()
        self.classe_filter.blockSignals(True)
        self.classe_filter.clear()
        self.classe_filter.addItem("Toutes les classes", None)
        classes = sorted(
            {
                (eleve.classe_id, eleve.classe_nom or f"Classe {eleve.classe_id}")
                for eleve in eleves
            },
            key=lambda item: item[1].casefold(),
        )
        for classe_id, classe_nom in classes:
            self.classe_filter.addItem(classe_nom, classe_id)
        class_index = self.classe_filter.findData(selected_class)
        self.classe_filter.setCurrentIndex(max(class_index, 0))
        self.classe_filter.blockSignals(False)
        self._apply_filters()

    def _get_eleves_and_finances(
        self,
    ) -> tuple[list[Eleve], dict[int, int], dict[int, str]]:
        """Charge les élèves actifs, puis calcule solde et statut."""
        eleves = self.eleve_service.list_eleves(actif_only=True)
        soldes = {
            eleve.id: self.paiement_service.calculer_solde(eleve.id, self.annee_id)
            for eleve in eleves
        }
        statuts = {
            eleve.id: self.paiement_service.calculer_statut(eleve.id, self.annee_id)
            for eleve in eleves
        }
        return eleves, soldes, statuts

    def _apply_filters(self, *_args: Any) -> None:
        """Filtre par classe, recherche textuelle et statut de paiement."""
        text = self.search_input.text().strip()
        classe_id: Optional[int] = self.classe_filter.currentData()
        if not text:
            success, results = run_service_operation(
                self,
                "la recherche des élèves",
                lambda: self.eleve_service.search_eleves(
                    classe_id=classe_id, actif_only=True
                ),
            )
            if not success or results is None:
                return
            eleves = results
        else:
            def search_all_fields() -> list[Eleve]:
                matches: dict[int, Eleve] = {}
                for criterion in ("nom", "prenom", "matricule"):
                    results = self.eleve_service.search_eleves(
                        **{criterion: text},
                        classe_id=classe_id,
                        actif_only=True,
                    )
                    matches.update((eleve.id, eleve) for eleve in results)
                return sorted(
                    matches.values(),
                    key=lambda eleve: (eleve.nom.casefold(), eleve.prenom.casefold()),
                )

            success, results = run_service_operation(
                self, "la recherche des élèves", search_all_fields
            )
            if not success or results is None:
                return
            eleves = results

        selected_status = self.statut_filter.currentText()
        if selected_status != "Tous les statuts":
            eleves = [
                eleve
                for eleve in eleves
                if self._statuts.get(eleve.id) == selected_status
            ]
        self.table_model.set_eleves(eleves, self._soldes, self._statuts)
        self._set_action_buttons_enabled(False)

    def _set_action_buttons_enabled(self, enabled: bool) -> None:
        """Active les actions qui nécessitent un élève sélectionné."""
        for button in (
            self.btn_modifier,
            self.btn_fiche,
            self.btn_payer,
            self.btn_archiver,
        ):
            button.setEnabled(enabled)

    def _on_selection_changed(self, *_args: Any) -> None:
        """Met à jour les actions disponibles selon la sélection."""
        selected = self.table_view.selectionModel().selectedRows()
        self._set_action_buttons_enabled(bool(selected))

    def _selected_eleve(self) -> Optional[Eleve]:
        """Retourne l'élève sélectionné dans la table."""
        selected = self.table_view.selectionModel().selectedRows()
        if not selected:
            return None
        return self.table_model.get_eleve_at(selected[0].row())

    def _on_ajouter(self) -> None:
        """Ouvre le formulaire de création d'un élève."""
        dialog = EleveFormDialog(self.conn, self)
        if dialog.exec():
            self._load_eleves()

    def _on_modifier(self) -> None:
        """Ouvre le formulaire de modification de l'élève sélectionné."""
        eleve = self._selected_eleve()
        if eleve is None:
            return
        dialog = EleveFormDialog(self.conn, self, eleve)
        if dialog.exec():
            self._load_eleves()

    def _on_fiche(self, *_args: Any) -> None:
        """Affiche la fiche détaillée de l'élève sélectionné."""
        eleve = self._selected_eleve()
        if eleve is not None:
            EleveDetailDialog(
                self.conn, eleve.id, self.annee_id, self
            ).exec()
            self._load_eleves()

    def _on_payer(self) -> None:
        """Ouvre le dialogue de paiement de l'élève sélectionné."""
        eleve = self._selected_eleve()
        if eleve is not None:
            dialog = PaiementDialog(self.conn, eleve.id, self.annee_id, self)
            if dialog.exec():
                self._load_eleves()

    def _on_archiver(self) -> None:
        """Confirme puis archive l'élève sélectionné."""
        eleve = self._selected_eleve()
        if eleve is None:
            return
        reply = QMessageBox.question(
            self,
            "Confirmer l'archivage",
            f"Archiver l'élève {eleve.nom_complet} ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        success, _ = run_service_operation(
            self,
            "l'archivage de l'élève",
            lambda: self.eleve_service.archive_eleve(eleve.id),
        )
        if success:
            self._load_eleves()
