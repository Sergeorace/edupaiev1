"""
Formulaire d'ajout/modification d'élève.
"""

from typing import Any, Optional

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
    QWidget,
)
from PySide6.QtCore import Qt, QDate

from services.eleve_service import EleveService
from models.eleve import Eleve
from ui.error_handling import run_service_operation


class EleveFormDialog(QDialog):
    """Dialogue de formulaire d'élève."""

    def __init__(
        self, conn: Any, parent: Optional[QWidget] = None, eleve: Optional[Eleve] = None
    ) -> None:
        """
        Initialise le dialogue.

        Args:
            conn: Connexion SQLite.
            parent: Widget parent.
            eleve: Élève à modifier (None pour ajout).
        """
        super().__init__(parent)
        self.conn = conn
        self.service = EleveService(conn)
        self.eleve = eleve
        self.annee_id = 1

        self.setWindowTitle("Ajouter un élève" if eleve is None else "Modifier l'élève")
        self.setMinimumWidth(500)

        self._setup_ui()
        self._load_classes()

        if eleve:
            self._load_eleve_data()
        else:
            # Générer automatiquement le matricule pour un nouvel élève
            self._generate_matricule()

    def _setup_ui(self) -> None:
        """Configure l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Matricule
        matricule_label = QLabel("Matricule")
        self.matricule_input = QLineEdit()
        self.matricule_input.setPlaceholderText("Ex: MAT001")
        layout.addWidget(matricule_label)
        layout.addWidget(self.matricule_input)

        # Nom
        nom_label = QLabel("Nom")
        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Nom de l'élève")
        layout.addWidget(nom_label)
        layout.addWidget(self.nom_input)

        # Prénom
        prenom_label = QLabel("Prénom")
        self.prenom_input = QLineEdit()
        self.prenom_input.setPlaceholderText("Prénom de l'élève")
        layout.addWidget(prenom_label)
        layout.addWidget(self.prenom_input)

        # Date de naissance
        naissance_label = QLabel("Date de naissance")
        self.naissance_input = QDateEdit()
        self.naissance_input.setCalendarPopup(True)
        self.naissance_input.setDate(QDate.currentDate())
        self.naissance_input.setMaximumDate(QDate.currentDate())
        layout.addWidget(naissance_label)
        layout.addWidget(self.naissance_input)

        # Sexe
        sexe_label = QLabel("Sexe")
        self.sexe_input = QComboBox()
        self.sexe_input.addItems(["M", "F"])
        layout.addWidget(sexe_label)
        layout.addWidget(self.sexe_input)

        # Classe
        classe_label = QLabel("Classe")
        self.classe_input = QComboBox()
        layout.addWidget(classe_label)
        layout.addWidget(self.classe_input)

        # Tuteur
        tuteur_label = QLabel("Tuteur")
        self.tuteur_input = QLineEdit()
        self.tuteur_input.setPlaceholderText("Nom du tuteur")
        layout.addWidget(tuteur_label)
        layout.addWidget(self.tuteur_input)

        # Téléphone
        telephone_label = QLabel("Téléphone")
        self.telephone_input = QLineEdit()
        self.telephone_input.setPlaceholderText("Numéro de téléphone")
        layout.addWidget(telephone_label)
        layout.addWidget(self.telephone_input)

        layout.addStretch()

        # Boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.btn_annuler = QPushButton("Annuler")
        self.btn_annuler.clicked.connect(self.reject)
        buttons_layout.addWidget(self.btn_annuler)

        self.btn_enregistrer = QPushButton("Enregistrer")
        self.btn_enregistrer.setObjectName("BtnAjouter")
        self.btn_enregistrer.clicked.connect(self._on_enregistrer)
        buttons_layout.addWidget(self.btn_enregistrer)

        layout.addLayout(buttons_layout)

    def _load_classes(self) -> None:
        """Charge la liste des classes depuis la base."""
        # Pour simplifier, on utilise des IDs fixes
        # Dans une vraie application, on chargerait depuis la base
        self.classes = {
            1: "6ème A",
            2: "6ème B",
            3: "5ème A",
            4: "4ème A",
        }
        for classe_id, classe_nom in self.classes.items():
            self.classe_input.addItem(classe_nom, classe_id)

    def _generate_matricule(self) -> None:
        """Génère automatiquement un matricule pour un nouvel élève."""
        try:
            # Récupérer tous les élèves pour trouver le dernier matricule
            eleves = self.service.list_eleves(actif_only=False)
            if eleves:
                # Extraire le numéro du dernier matricule et l'incrémenter
                last_matricule = max(e.matricule for e in eleves)
                # Format: MAT001, MAT002, etc.
                last_num = int(last_matricule.replace("MAT", ""))
                new_num = last_num + 1
                new_matricule = f"MAT{new_num:03d}"
            else:
                new_matricule = "MAT001"
            self.matricule_input.setText(new_matricule)
            self.matricule_input.setReadOnly(True)  # Rendre le champ en lecture seule
        except Exception:
            # En cas d'erreur, laisser le champ vide
            self.matricule_input.setReadOnly(False)

    def _load_eleve_data(self) -> None:
        """Charge les données de l'élève dans le formulaire."""
        if self.eleve:
            self.matricule_input.setText(self.eleve.matricule)
            self.matricule_input.setReadOnly(False)  # Modifiable lors de la modification
            self.nom_input.setText(self.eleve.nom)
            self.prenom_input.setText(self.eleve.prenom)
            self.naissance_input.setDate(
                QDate.fromString(str(self.eleve.date_naissance), Qt.DateFormat.ISODate)
            )
            self.sexe_input.setCurrentText(self.eleve.sexe)
            self.classe_input.setCurrentText(self.eleve.classe_nom or "")
            self.tuteur_input.setText(self.eleve.tuteur)
            self.telephone_input.setText(self.eleve.telephone)

    def _on_enregistrer(self) -> None:
        """Gère l'enregistrement de l'élève."""
        matricule = self.matricule_input.text().strip()
        nom = self.nom_input.text().strip()
        prenom = self.prenom_input.text().strip()
        date_naissance = self.naissance_input.date().toPython()
        sexe = self.sexe_input.currentText()
        classe_id = self.classe_input.currentData()
        tuteur = self.tuteur_input.text().strip()
        telephone = self.telephone_input.text().strip()

        if self.eleve is not None:
            success, _ = run_service_operation(
                self,
                "la modification de l'élève",
                lambda: self.service.update_eleve(
                    self.eleve.id,
                    matricule,
                    nom,
                    prenom,
                    date_naissance,
                    sexe,
                    classe_id,
                    tuteur,
                    telephone,
                ),
            )
            message = "L'élève a été modifié avec succès."
        else:
            success, _ = run_service_operation(
                self,
                "la création de l'élève",
                lambda: self.service.create_eleve(
                    matricule,
                    nom,
                    prenom,
                    date_naissance,
                    sexe,
                    classe_id,
                    tuteur,
                    telephone,
                ),
            )
            message = "L'élève a été ajouté avec succès."

        if success:
            QMessageBox.information(self, "Succès", message)
            self.accept()
