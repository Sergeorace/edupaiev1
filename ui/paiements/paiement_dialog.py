"""Dialogue de saisie d'un paiement scolaire."""

from typing import Any, Optional

from PySide6.QtCore import QDate, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from services.paiement_service import PaiementService
from ui.error_handling import run_service_operation
from utils.formatters import format_montant


class PaiementDialog(QDialog):
    """Dialogue de saisie et validation d'un paiement."""

    paiement_enregistre = Signal(int)

    def __init__(
        self,
        conn: Any,
        eleve_id: int,
        annee_id: int,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialise les champs et charge le solde de l'élève."""
        super().__init__(parent)
        self.service = PaiementService(conn)
        self.eleve_id = eleve_id
        self.annee_id = annee_id
        self.solde_actuel = 0
        self.setWindowTitle("Enregistrer un paiement")
        self.setMinimumWidth(480)
        self._setup_ui()
        self._load_solde()

    def _setup_ui(self) -> None:
        """Construit le formulaire de paiement."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Nouveau paiement")
        title.setObjectName("title")
        layout.addWidget(title)

        self.lbl_solde_avant = QLabel()
        self.lbl_solde_avant.setObjectName("balanceBefore")
        layout.addWidget(self.lbl_solde_avant)

        montant_layout = QHBoxLayout()
        montant_layout.addWidget(QLabel("Montant *"))
        self.montant_input = QLineEdit()
        self.montant_input.setObjectName("paymentAmount")
        self.montant_input.setPlaceholderText("Montant entier en FCFA")
        self.montant_input.setClearButtonEnabled(True)
        self.montant_input.textChanged.connect(self._validate_form)
        montant_layout.addWidget(self.montant_input, stretch=1)
        layout.addLayout(montant_layout)

        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date *"))
        self.date_input = QDateEdit()
        self.date_input.setObjectName("paymentDate")
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setMaximumDate(QDate.currentDate())
        self.date_input.dateChanged.connect(self._validate_form)
        date_layout.addWidget(self.date_input, stretch=1)
        layout.addLayout(date_layout)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode de paiement *"))
        self.mode_input = QComboBox()
        self.mode_input.setObjectName("paymentMode")
        self.mode_input.addItems(["Espèces", "Chèque", "Virement", "Mobile"])
        self.mode_input.currentTextChanged.connect(self._validate_form)
        mode_layout.addWidget(self.mode_input, stretch=1)
        layout.addLayout(mode_layout)

        motif_layout = QHBoxLayout()
        motif_layout.addWidget(QLabel("Motif"))
        self.motif_input = QLineEdit()
        self.motif_input.setObjectName("paymentReason")
        self.motif_input.setPlaceholderText("Facultatif")
        motif_layout.addWidget(self.motif_input, stretch=1)
        layout.addLayout(motif_layout)

        self.validation_label = QLabel()
        self.validation_label.setObjectName("validationMessage")
        self.validation_label.setWordWrap(True)
        layout.addWidget(self.validation_label)

        self.lbl_solde_apres = QLabel()
        self.lbl_solde_apres.setObjectName("balanceAfter")
        layout.addWidget(self.lbl_solde_apres)
        layout.addStretch()

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        self.btn_annuler = QPushButton("Fermer")
        self.btn_annuler.clicked.connect(self.reject)
        buttons_layout.addWidget(self.btn_annuler)
        self.btn_enregistrer = QPushButton("Enregistrer le paiement")
        self.btn_enregistrer.setObjectName("successButton")
        self.btn_enregistrer.setEnabled(False)
        self.btn_enregistrer.clicked.connect(self._on_enregistrer)
        buttons_layout.addWidget(self.btn_enregistrer)
        layout.addLayout(buttons_layout)

    def _load_solde(self) -> None:
        """Récupère le solde courant via le service des paiements."""
        success, solde = run_service_operation(
            self,
            "le chargement du solde",
            lambda: self.service.calculer_solde(self.eleve_id, self.annee_id),
        )
        if not success or solde is None:
            self.reject()
            return
        self.solde_actuel = solde
        self.lbl_solde_avant.setText(
            f"Solde restant avant paiement : {format_montant(solde)}"
        )
        self._validate_form()

    def _validate_form(self, *_args: Any) -> None:
        """Valide le montant et affiche le solde calculé avant/après paiement."""
        raw_amount = self.montant_input.text().strip()
        amount: Optional[int] = None
        message = ""
        if raw_amount:
            if not raw_amount.isdecimal():
                message = "Saisissez un montant entier positif."
            else:
                amount = int(raw_amount)
                if amount <= 0:
                    message = "Le montant doit être supérieur à 0."
                elif amount > self.solde_actuel:
                    message = (
                        f"Le montant dépasse le solde restant "
                        f"({format_montant(self.solde_actuel)})."
                    )

        self.validation_label.setText(message)
        valid = (
            amount is not None
            and amount > 0
            and amount <= self.solde_actuel
            and self.date_input.date() <= QDate.currentDate()
            and bool(self.mode_input.currentText())
        )
        self.btn_enregistrer.setEnabled(valid)
        if amount is not None and amount > 0:
            self.lbl_solde_apres.setText(
                f"Solde après paiement : {format_montant(self.solde_actuel - amount)}"
            )
        else:
            self.lbl_solde_apres.setText(
                f"Solde après paiement : {format_montant(self.solde_actuel)}"
            )

    def _on_enregistrer(self) -> None:
        """Enregistre le paiement ou affiche le message métier retourné."""
        raw_amount = self.montant_input.text().strip()
        if not raw_amount.isdecimal():
            self._validate_form()
            return

        success, paiement = run_service_operation(
            self,
            "l'enregistrement du paiement",
            lambda: self.service.enregistrer_paiement(
                self.eleve_id,
                self.annee_id,
                int(raw_amount),
                self.date_input.date().toPython(),
                self.mode_input.currentText(),
                self.motif_input.text().strip() or None,
            ),
        )
        if success and paiement is not None:
            QMessageBox.information(
                self, "Paiement enregistré", "Le paiement a été enregistré."
            )
            self.paiement_enregistre.emit(paiement.id)
            self.accept()
