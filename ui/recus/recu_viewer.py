"""
Widget de visualisation et gestion des reçus.
"""

from typing import Any, Optional
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QFileDialog,
    QMenu,
    QWidget,
    QLabel,
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QAction

from services.recu_service import RecuService
from services.paiement_service import PaiementService
from models.paiement import Paiement
from models.recu import Recu
from utils.formatters import format_montant, format_date
from reports.recu_generator import generer_pdf_recu
from ui.error_handling import run_service_operation
from utils.date_utils import parse_date


class RecusViewerWidget(QWidget):
    """Widget de visualisation des reçus."""

    def __init__(self, conn: Any, parent: Optional[QWidget] = None) -> None:
        """
        Initialise le widget de visualisation des reçus.

        Args:
            conn: Connexion SQLite à utiliser.
        """
        super().__init__(parent)
        self.conn = conn
        self.recu_service = RecuService(conn)
        self.paiement_service = PaiementService(conn)
        self.annee_id = 1  # Année scolaire 2025-2026

        self.recu_ids = []
        self.paiement_ids = []

        self._setup_ui()
        self._load_recus()

    def _setup_ui(self) -> None:
        """Configure l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # Titre
        title = QLabel("Gestion des reçus")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        # Barre de recherche
        search_layout = QHBoxLayout()
        search_layout.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("Rechercher (numéro, élève)...")
        self.search_input.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_input, stretch=1)

        self.btn_rechercher = QPushButton("Rechercher")
        self.btn_rechercher.clicked.connect(self._on_search_changed)
        search_layout.addWidget(self.btn_rechercher)

        layout.addLayout(search_layout)

        # Tableau des reçus
        self.table_recus = QTableWidget()
        self.table_recus.setColumnCount(9)
        self.table_recus.setHorizontalHeaderLabels(
            ["Numéro", "Élève", "Classe", "Montant", "Date paiement", "Date reçu", "Statut", "Actions"]
        )
        self.table_recus.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_recus.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table_recus.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_recus.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_recus.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_recus.horizontalHeader().setSectionResizeMode(
            5, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_recus.horizontalHeader().setSectionResizeMode(
            6, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_recus.horizontalHeader().setSectionResizeMode(
            7, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_recus.horizontalHeader().setSectionResizeMode(
            8, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table_recus.setAlternatingRowColors(True)
        self.table_recus.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_recus.customContextMenuRequested.connect(self._show_context_menu)
        self.table_recus.doubleClicked.connect(self._on_double_click)
        layout.addWidget(self.table_recus)

        # Boutons d'action
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.btn_exporter = QPushButton("📥 Télécharger PDF")
        self.btn_exporter.clicked.connect(self._on_exporter_pdf)
        self.btn_exporter.setEnabled(False)
        buttons_layout.addWidget(self.btn_exporter)

        self.btn_imprimer = QPushButton("🖨️ Imprimer")
        self.btn_imprimer.clicked.connect(self._on_imprimer)
        self.btn_imprimer.setEnabled(False)
        buttons_layout.addWidget(self.btn_imprimer)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        # Connecter la sélection
        self.table_recus.itemSelectionChanged.connect(self._on_selection_changed)

    def _load_recus(self, search_text: str = "") -> None:
        """
        Charge la liste des reçus.

        Args:
            search_text: Texte de recherche (numéro ou nom d'élève).
        """
        def get_filtered_recus() -> tuple[
            list[Recu], dict[int, Optional[Paiement]]
        ]:
            recus = self.recu_service.get_recus_by_annee(self.annee_id)
            if search_text:
                search_lower = search_text.lower()
                filtered = []
                for recu in recus:
                    donnees = recu.get_donnees()
                    if (
                        search_lower in recu.numero.lower()
                        or search_lower in donnees.get("nom", "").casefold()
                        or search_lower in donnees.get("classe", "").casefold()
                    ):
                        filtered.append(recu)
                recus = filtered
            paiements = {
                recu.paiement_id: self.paiement_service.get_paiement_by_id(
                    recu.paiement_id
                )
                for recu in recus
            }
            return recus, paiements

        success, result = run_service_operation(
            self, "le chargement des reçus", get_filtered_recus
        )
        if success and result is not None:
            recus, paiements = result
            self._update_recus_table(recus, paiements)

    def _update_recus_table(
        self,
        recus: list[Recu],
        paiements: dict[int, Optional[Paiement]],
    ) -> None:
        """
        Met à jour le tableau des reçus.

        Args:
            recus: Liste des reçus.
        """
        self.table_recus.setRowCount(len(recus))
        self.recu_ids = []
        self.paiement_ids = []

        for row, recu in enumerate(recus):
            self.recu_ids.append(recu.id)
            self.paiement_ids.append(recu.paiement_id)

            donnees = recu.get_donnees()

            # Numéro
            numero_item = QTableWidgetItem(recu.numero)
            numero_item.setForeground(Qt.GlobalColor.blue)
            self.table_recus.setItem(row, 0, numero_item)

            # Élève
            eleve_item = QTableWidgetItem(donnees.get("nom", ""))
            self.table_recus.setItem(row, 1, eleve_item)

            # Classe
            classe_item = QTableWidgetItem(donnees.get("classe", ""))
            self.table_recus.setItem(row, 2, classe_item)

            # Montant
            montant_item = QTableWidgetItem(format_montant(donnees.get("montant", 0)))
            montant_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table_recus.setItem(row, 3, montant_item)

            # Date paiement
            date_paiement = donnees.get("date_paiement", "")
            date_paiement_item = QTableWidgetItem(date_paiement)
            self.table_recus.setItem(row, 4, date_paiement_item)

            # Date reçu
            date_recu = (
                datetime.fromisoformat(recu.date_generation).strftime("%d/%m/%Y %H:%M")
                if recu.date_generation
                else ""
            )
            date_recu_item = QTableWidgetItem(date_recu)
            self.table_recus.setItem(row, 5, date_recu_item)

            # Statut du paiement
            paiement = paiements.get(recu.paiement_id)
            if paiement:
                statut_item = QTableWidgetItem(
                    "Annulé" if paiement.statut == "annule" else "Valide"
                )
                if paiement.statut == "annule":
                    statut_item.setForeground(Qt.GlobalColor.red)
                self.table_recus.setItem(row, 6, statut_item)
            else:
                statut_item = QTableWidgetItem("Inconnu")
                self.table_recus.setItem(row, 6, statut_item)

            # Boutons d'action dans le tableau
            widget_actions = QWidget()
            layout_actions = QHBoxLayout(widget_actions)
            layout_actions.setContentsMargins(5, 2, 5, 2)
            layout_actions.setSpacing(5)

            btn_download = QPushButton("📥")
            btn_download.setFixedSize(30, 25)
            btn_download.setToolTip("Télécharger PDF")
            btn_download.clicked.connect(lambda _, r=row: self._download_row(r))
            layout_actions.addWidget(btn_download)

            btn_print = QPushButton("🖨️")
            btn_print.setFixedSize(30, 25)
            btn_print.setToolTip("Imprimer")
            btn_print.clicked.connect(lambda _, r=row: self._print_row(r))
            layout_actions.addWidget(btn_print)

            self.table_recus.setCellWidget(row, 7, widget_actions)

    def _on_search_changed(self) -> None:
        """Gère le changement de texte de recherche."""
        search_text = self.search_input.text().strip()
        self._load_recus(search_text)

    def _on_selection_changed(self) -> None:
        """Gère le clic sur le tableau."""
        selected = self.table_recus.selectionModel().selectedRows()
        has_selection = len(selected) > 0

        self.btn_exporter.setEnabled(has_selection)
        self.btn_imprimer.setEnabled(has_selection)

    def _on_double_click(self) -> None:
        """Gère le double-clic sur le tableau pour télécharger le PDF."""
        self._on_exporter_pdf()

    def _download_row(self, row: int) -> None:
        """Télécharge le PDF pour une ligne spécifique."""
        # Sélectionner la ligne
        self.table_recus.selectRow(row)
        self._on_exporter_pdf()

    def _print_row(self, row: int) -> None:
        """Imprime le PDF pour une ligne spécifique."""
        # Sélectionner la ligne
        self.table_recus.selectRow(row)
        self._on_imprimer()

    def _show_context_menu(self, position: QPoint) -> None:
        """
        Affiche le menu contextuel.

        Args:
            position: Position du clic.
        """
        selected = self.table_recus.selectionModel().selectedRows()
        if not selected:
            return

        menu = QMenu(self)

        action_exporter = QAction("📥 Exporter PDF", self)
        action_exporter.triggered.connect(self._on_exporter_pdf)
        menu.addAction(action_exporter)

        action_imprimer = QAction("🖨️ Imprimer", self)
        action_imprimer.triggered.connect(self._on_imprimer)
        menu.addAction(action_imprimer)

        menu.exec(self.table_recus.mapToGlobal(position))

    def _get_selected_recu(
        self,
    ) -> tuple[Optional[Recu], Optional[Paiement]]:
        """
        Récupère le reçu sélectionné.

        Returns:
            Tuple (recu, paiement) ou (None, None).
        """
        selected = self.table_recus.selectionModel().selectedRows()
        if not selected:
            return None, None

        row = selected[0].row()
        if row < 0 or row >= len(self.recu_ids):
            return None, None

        recu_id = self.recu_ids[row]
        paiement_id = self.paiement_ids[row]

        success, result = run_service_operation(
            self,
            "la récupération du reçu",
            lambda: (
                self.recu_service.get_recu_by_id(recu_id),
                self.paiement_service.get_paiement_by_id(paiement_id),
            ),
        )
        return result if success and result is not None else (None, None)

    def _on_exporter_pdf(self) -> None:
        """Gère l'export en PDF."""
        recu, paiement = self._get_selected_recu()
        if not recu:
            return

        def export_recu() -> Optional[Path]:
            # Demander le chemin de sauvegarde
            default_name = f"recu_{recu.numero}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Enregistrer le reçu",
                str(Path.home() / "Desktop" / default_name),
                "Fichiers PDF (*.pdf)",
            )

            if not file_path:
                return None

            # Déterminer le statut du paiement
            statut_paiement = "valide"
            if paiement and paiement.statut == "annule":
                statut_paiement = "annulé"

            # Générer le PDF
            output_path = generer_pdf_recu(
                recu.donnees_json,
                recu.numero,
                recu.date_generation,
                statut_paiement,
                Path(file_path),
            )

            # Vérifier que le fichier a été créé
            if output_path and output_path.exists():
                return output_path
            else:
                raise RuntimeError("Le fichier PDF n'a pas été créé")

        success, file_path = run_service_operation(
            self, "l'export PDF du reçu", export_recu
        )
        if success and file_path is not None:
            QMessageBox.information(
                self, "Succès", f"Le reçu a été exporté avec succès :\n{file_path}"
            )

    def _on_imprimer(self) -> None:
        """Gère l'impression du reçu."""
        recu, paiement = self._get_selected_recu()
        if not recu:
            return

        def print_recu() -> None:
            # Générer le PDF dans le dossier temporaire
            import tempfile
            import subprocess
            import platform

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                temp_path = Path(tmp.name)

            try:
                statut_paiement = (
                    "annulé" if paiement and paiement.statut == "annule" else "valide"
                )
                generer_pdf_recu(
                    recu.donnees_json,
                    recu.numero,
                    recu.date_generation,
                    statut_paiement,
                    temp_path,
                )

                # Ouvrir le PDF avec le visualiseur par défaut du système
                # Cela permet à l'utilisateur d'imprimer via le visualiseur
                if platform.system() == "Windows":
                    subprocess.Popen(["start", "", str(temp_path)], shell=True)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.Popen(["open", str(temp_path)])
                else:  # Linux
                    subprocess.Popen(["xdg-open", str(temp_path)])

                QMessageBox.information(
                    self,
                    "Impression",
                    "Le PDF a été ouvert. Utilisez le visualiseur PDF pour imprimer.",
                )
            except Exception as e:
                raise e
            finally:
                # Le fichier temporaire sera supprimé automatiquement par le système
                # après fermeture du visualiseur
                pass

        run_service_operation(self, "l'impression du reçu", print_recu)


def open_recu_direct(
    conn: Any, paiement_id: int, parent: Optional[QWidget] = None
) -> None:
    """
    Ouvre directement le reçu d'un paiement.

    Args:
        conn: Connexion SQLite.
        paiement_id: ID du paiement.
    """
    recu_service = RecuService(conn)
    def fetch_recu_and_payment():
        recu = recu_service.get_recu_by_paiement(paiement_id)
        paiement = PaiementService(conn).get_paiement_by_id(paiement_id)
        return recu, paiement

    success, result = run_service_operation(
        parent,
        "la récupération du reçu",
        fetch_recu_and_payment,
    )
    if not success or result is None:
        return
    recu, paiement = result
    if recu is None:
        QMessageBox.warning(parent, "Reçu introuvable", "Aucun reçu trouvé.")
        return

    def export_recu() -> Optional[Path]:
        # Demander le chemin de sauvegarde
        default_name = f"recu_{recu.numero}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Enregistrer le reçu",
            str(Path.home() / "Desktop" / default_name),
            "Fichiers PDF (*.pdf)",
        )

        if not file_path:
            return None

        # Générer le PDF
        return generer_pdf_recu(
            recu.donnees_json,
            recu.numero,
            recu.date_generation,
            "annulé" if paiement and paiement.statut == "annule" else "valide",
            Path(file_path),
        )

    success, file_path = run_service_operation(
        parent, "l'export PDF du reçu", export_recu
    )
    if success and file_path is not None:
        QMessageBox.information(
            parent,
            "Succès",
            f"Le reçu a été exporté :\n{file_path}",
        )
