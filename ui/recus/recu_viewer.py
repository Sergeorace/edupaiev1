"""
Widget de visualisation et gestion des reçus.
"""

import sqlite3
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QFileDialog,
    QPrintDialog,
    QMenu,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtPrintSupport import QPrinter

from services.recu_service import RecuService
from services.paiement_service import PaiementService
from utils.formatters import format_montant, format_date
from reports.recu_generator import generer_pdf_recu


class RecusViewerWidget(QWidget):
    """Widget de visualisation des reçus."""

    def __init__(self, conn: sqlite3.Connection):
        """
        Initialise le widget de visualisation des reçus.

        Args:
            conn: Connexion SQLite à utiliser.
        """
        super().__init__()
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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Titre
        title = QPushButton("📄 Gestion des reçus")
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

        # Barre de recherche
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher (numéro, élève)...")
        self.search_input.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_input, stretch=1)

        self.btn_rechercher = QPushButton("🔍 Rechercher")
        self.btn_rechercher.clicked.connect(self._on_search_changed)
        search_layout.addWidget(self.btn_rechercher)

        layout.addLayout(search_layout)

        # Tableau des reçus
        self.table_recus = QTableWidget()
        self.table_recus.setColumnCount(7)
        self.table_recus.setHorizontalHeaderLabels(
            ["Numéro", "Élève", "Classe", "Montant", "Date paiement", "Date reçu", "Statut"]
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
        self.table_recus.setAlternatingRowColors(True)
        self.table_recus.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_recus.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.table_recus)

        # Boutons d'action
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.btn_exporter = QPushButton("📥 Exporter PDF")
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
        try:
            recus = self.recu_service.get_recus_by_annee(self.annee_id)

            # Filtrer par recherche
            if search_text:
                search_lower = search_text.lower()
                filtered = []
                for recu in recus:
                    donnees = recu.donnees_json
                    if (
                        search_lower in recu.numero.lower()
                        or search_lower in donnees.get("nom", "").lower()
                        or search_lower in donnees.get("classe", "").lower()
                    ):
                        filtered.append(recu)
                recus = filtered

            self._update_recus_table(recus)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors du chargement des reçus: {str(e)}",
            )

    def _update_recus_table(self, recus: list) -> None:
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

            donnees = recu.donnees_json

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
            date_paiement_item = QTableWidgetItem(donnees.get("date_paiement", ""))
            self.table_recus.setItem(row, 4, date_paiement_item)

            # Date reçu
            date_recu = datetime.fromisoformat(recu.date_generation).strftime("%d/%m/%Y %H:%M")
            date_recu_item = QTableWidgetItem(date_recu)
            self.table_recus.setItem(row, 5, date_recu_item)

            # Statut du paiement
            paiement = self.paiement_service.get_paiement_by_id(recu.paiement_id)
            if paiement:
                statut_item = QTableWidgetItem(paiement.statut.capitalize())
                if paiement.statut == "annulé":
                    statut_item.setForeground(Qt.GlobalColor.red)
                self.table_recus.setItem(row, 6, statut_item)
            else:
                statut_item = QTableWidgetItem("Inconnu")
                self.table_recus.setItem(row, 6, statut_item)

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

    def _show_context_menu(self, position) -> None:
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

    def _get_selected_recu(self):
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

        recu = self.recu_service.get_recu_by_id(recu_id)
        paiement = self.paiement_service.get_paiement_by_id(paiement_id)

        return recu, paiement

    def _on_exporter_pdf(self) -> None:
        """Gère l'export en PDF."""
        recu, paiement = self._get_selected_recu()
        if not recu:
            return

        try:
            # Demander le chemin de sauvegarde
            default_name = f"recu_{recu.numero}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Enregistrer le reçu",
                str(Path.home() / "Desktop" / default_name),
                "Fichiers PDF (*.pdf)",
            )

            if not file_path:
                return

            # Générer le PDF
            statut_paiement = paiement.statut if paiement else "valide"
            generer_pdf_recu(
                recu.donnees_json,
                recu.numero,
                recu.date_generation,
                statut_paiement,
                Path(file_path),
            )

            QMessageBox.information(
                self,
                "Succès",
                f"Le reçu a été exporté avec succès :\n{file_path}",
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'export PDF: {str(e)}",
            )

    def _on_imprimer(self) -> None:
        """Gère l'impression du reçu."""
        recu, paiement = self._get_selected_recu()
        if not recu:
            return

        try:
            # Générer le PDF temporaire
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                temp_path = Path(tmp.name)

            statut_paiement = paiement.statut if paiement else "valide"
            generer_pdf_recu(
                recu.donnees_json,
                recu.numero,
                recu.date_generation,
                statut_paiement,
                temp_path,
            )

            # Ouvrir la boîte de dialogue d'impression
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            dialog = QPrintDialog(printer, self)

            if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                # Imprimer le PDF
                from PySide6.QtGui import QTextDocument

                doc = QTextDocument()
                doc.setHtml(f"<iframe src='{temp_path}'></iframe>")
                doc.print(printer)

            # Supprimer le fichier temporaire
            temp_path.unlink(missing_ok=True)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'impression: {str(e)}",
            )


def open_recu_direct(conn: sqlite3.Connection, paiement_id: int) -> None:
    """
    Ouvre directement le reçu d'un paiement.

    Args:
        conn: Connexion SQLite.
        paiement_id: ID du paiement.
    """
    recu_service = RecuService(conn)
    recu = recu_service.get_recu_by_paiement(paiement_id)

    if not recu:
        QMessageBox.critical(None, "Erreur", "Aucun reçu trouvé pour ce paiement.")
        return

    try:
        # Demander le chemin de sauvegarde
        default_name = f"recu_{recu.numero}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Enregistrer le reçu",
            str(Path.home() / "Desktop" / default_name),
            "Fichiers PDF (*.pdf)",
        )

        if not file_path:
            return

        # Générer le PDF
        paiement_service = PaiementService(conn)
        paiement = paiement_service.get_paiement_by_id(paiement_id)
        statut_paiement = paiement.statut if paiement else "valide"

        generer_pdf_recu(
            recu.donnees_json,
            recu.numero,
            recu.date_generation,
            statut_paiement,
            Path(file_path),
        )

        QMessageBox.information(
            None,
            "Succès",
            f"Le reçu a été exporté avec succès :\n{file_path}",
        )

    except Exception as e:
        QMessageBox.critical(
            None,
            "Erreur",
            f"Erreur lors de l'export PDF: {str(e)}",
        )
