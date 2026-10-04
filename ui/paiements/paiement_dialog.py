"""
Dialogue d'enregistrement de paiement.
"""

import sqlite3
from datetime import date
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QDateEdit,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Qt, QDate

from services.paiement_service import PaiementService
from utils.formatters import format_montant


class PaiementDialog(QDialog):
    """Dialogue d'enregistrement de paiement."""

    def __init__(self, conn: sqlite3.Connection, eleve_id: int, annee_id: int):
        """
        Initialise le dialogue.

        Args:
            conn: Connexion SQLite.
            eleve_id: ID de l'élève.
            annee_id: ID de l'année scolaire.
        """
        super().__init__()
        self.conn = conn
        self.service = PaiementService(conn)
        self.eleve_id = eleve_id
        self.annee_id = annee_id

        self.setWindowTitle("Enregistrer un paiement")
        self.setMinimumWidth(500)

        self._setup_ui()
        self._load_solde()

    def _setup_ui(self) -> None:
        """Configure l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Solde avant
        self.lbl_solde_avant = QLabel()
        self.lbl_solde_avant.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.lbl_solde_avant)

        # Montant
        montant_layout = QHBoxLayout()
        montant_label = QLabel("Montant *")
        montant_label.setObjectName("required")
        self.montant_input = QLineEdit()
        self.montant_input.setPlaceholderText("Montant en FCFA")
        self.montant_input.textChanged.connect(self._validate_form)
        montant_layout.addWidget(montant_label)
        montant_layout.addWidget(self.montant_input)
        layout.addLayout(montant_layout)

        # Date
        date_layout = QHBoxLayout()
        date_label = QLabel("Date *")
        date_label.setObjectName("required")
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.dateChanged.connect(self._validate_form)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_input)
        layout.addLayout(date_layout)

        # Mode de paiement
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Mode *")
        mode_label.setObjectName("required")
        self.mode_input = QComboBox()
        self.mode_input.addItems(["Espèces", "Chèque", "Virement", "Mobile"])
        self.mode_input.currentTextChanged.connect(self._validate_form)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_input)
        layout.addLayout(mode_layout)

        # Motif
        motif_layout = QHBoxLayout()
        motif_label = QLabel("Motif")
        self.motif_input = QLineEdit()
        self.motif_input.setPlaceholderText("Optionnel")
        motif_layout.addWidget(motif_label)
        motif_layout.addWidget(self.motif_input)
        layout.addLayout(motif_layout)

        # Solde après
        self.lbl_solde_apres = QLabel()
        self.lbl_solde_apres.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.lbl_solde_apres)

        layout.addStretch()

        # Boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.btn_annuler = QPushButton("Annuler")
        self.btn_annuler.clicked.connect(self.reject)
        buttons_layout.addWidget(self.btn_annuler)

        self.btn_enregistrer = QPushButton("Enregistrer")
        self.btn_enregistrer.setObjectName("successButton")
        self.btn_enregistrer.clicked.connect(self._on_enregistrer)
        self.btn_enregistrer.setEnabled(False)
        buttons_layout.addWidget(self.btn_enregistrer)

        layout.addLayout(buttons_layout)

    def _load_solde(self) -> None:
        """Charge le solde actuel de l'élève."""
        try:
            self.solde_actuel = self.service.calculer_solde(self.eleve_id, self.annee_id)
            self.lbl_solde_avant.setText(f"Solde restant: {format_montant(self.solde_actuel)}")
            self._update_solde_apres()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement du solde: {str(e)}")
            self.reject()

    def _update_solde_apres(self) -> None:
        """Met à jour l'affichage du solde après paiement."""
        try:
            montant_text = self.montant_input.text().strip()
            if montant_text:
                montant = int(montant_text)
                nouveau_solde = self.solde_actuel - montant
                self.lbl_solde_apres.setText(
                    f"Solde après paiement: {format_montant(nouveau_solde)}"
                )
            else:
                self.lbl_solde_apres.setText(f"Solde après paiement: {format_montant(self.solde_actuel)}")
        except ValueError:
            self.lbl_solde_apres.setText("Solde après paiement: -")

    def _validate_form(self) -> None:
        """Valide le formulaire et active/désactive le bouton."""
        montant_text = self.montant_input.text().strip()
        date_valide = self.date_input.date() <= QDate.currentDate()
        mode_valide = self.mode_input.currentText() != ""

        try:
            if montant_text:
                montant = int(montant_text)
                montant_valide = montant > 0
            else:
                montant_valide = False
        except ValueError:
            montant_valide = False

        self.btn_enregistrer.setEnabled(montant_valide and date_valide and mode_valide)
        self._update_solde_apres()

    def _on_enregistrer(self) -> None:
        """Gère l'enregistrement du paiement."""
        try:
            montant = int(self.montant_input.text().strip())
            date_paiement = self.date_input.date().toPython()
            mode_paiement = self.mode_input.currentText()
            motif = self.motif_input.text().strip() or None

            self.service.enregistrer_paiement(
                self.eleve_id,
                self.annee_id,
                montant,
                date_paiement,
                mode_paiement,
                motif,
            )

            QMessageBox.information(self, "Succès", "Le paiement a été enregistré avec succès.")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
