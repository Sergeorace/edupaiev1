"""
Formulaire d'ajout/modification d'élève.
"""

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

from services.eleve_service import EleveService
from models.eleve import Eleve


class EleveFormDialog(QDialog):
    """Dialogue de formulaire d'élève."""

    def __init__(self, conn: sqlite3.Connection, parent=None, eleve: Eleve = None):
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

    def _setup_ui(self) -> None:
        """Configure l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Matricule
        matricule_layout = QHBoxLayout()
        matricule_label = QLabel("Matricule *")
        matricule_label.setObjectName("required")
        self.matricule_input = QLineEdit()
        matricule_layout.addWidget(matricule_label)
        matricule_layout.addWidget(self.matricule_input)
        layout.addLayout(matricule_layout)

        # Nom
        nom_layout = QHBoxLayout()
        nom_label = QLabel("Nom *")
        nom_label.setObjectName("required")
        self.nom_input = QLineEdit()
        nom_layout.addWidget(nom_label)
        nom_layout.addWidget(self.nom_input)
        layout.addLayout(nom_layout)

        # Prénom
        prenom_layout = QHBoxLayout()
        prenom_label = QLabel("Prénom *")
        prenom_label.setObjectName("required")
        self.prenom_input = QLineEdit()
        prenom_layout.addWidget(prenom_label)
        prenom_layout.addWidget(self.prenom_input)
        layout.addLayout(prenom_layout)

        # Date de naissance
        naissance_layout = QHBoxLayout()
        naissance_label = QLabel("Date de naissance *")
        naissance_label.setObjectName("required")
        self.naissance_input = QDateEdit()
        self.naissance_input.setCalendarPopup(True)
        self.naissance_input.setDate(QDate.currentDate())
        naissance_layout.addWidget(naissance_label)
        naissance_layout.addWidget(self.naissance_input)
        layout.addLayout(naissance_layout)

        # Sexe
        sexe_layout = QHBoxLayout()
        sexe_label = QLabel("Sexe *")
        sexe_label.setObjectName("required")
        self.sexe_input = QComboBox()
        self.sexe_input.addItems(["M", "F"])
        sexe_layout.addWidget(sexe_label)
        sexe_layout.addWidget(self.sexe_input)
        layout.addLayout(sexe_layout)

        # Classe
        classe_layout = QHBoxLayout()
        classe_label = QLabel("Classe *")
        classe_label.setObjectName("required")
        self.classe_input = QComboBox()
        classe_layout.addWidget(classe_label)
        classe_layout.addWidget(self.classe_input)
        layout.addLayout(classe_layout)

        # Tuteur
        tuteur_layout = QHBoxLayout()
        tuteur_label = QLabel("Tuteur *")
        tuteur_label.setObjectName("required")
        self.tuteur_input = QLineEdit()
        tuteur_layout.addWidget(tuteur_label)
        tuteur_layout.addWidget(self.tuteur_input)
        layout.addLayout(tuteur_layout)

        # Téléphone
        telephone_layout = QHBoxLayout()
        telephone_label = QLabel("Téléphone *")
        telephone_label.setObjectName("required")
        self.telephone_input = QLineEdit()
        telephone_layout.addWidget(telephone_label)
        telephone_layout.addWidget(self.telephone_input)
        layout.addLayout(telephone_layout)

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

    def _load_eleve_data(self) -> None:
        """Charge les données de l'élève dans le formulaire."""
        if self.eleve:
            self.matricule_input.setText(self.eleve.matricule)
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
        try:
            matricule = self.matricule_input.text().strip()
            nom = self.nom_input.text().strip()
            prenom = self.prenom_input.text().strip()
            date_naissance = self.naissance_input.date().toPython()
            sexe = self.sexe_input.currentText()
            classe_id = self.classe_input.currentData()
            tuteur = self.tuteur_input.text().strip()
            telephone = self.telephone_input.text().strip()

            if self.eleve:
                # Modification
                self.service.update_eleve(
                    self.eleve.id,
                    matricule,
                    nom,
                    prenom,
                    date_naissance,
                    sexe,
                    classe_id,
                    tuteur,
                    telephone,
                )
                QMessageBox.information(self, "Succès", "L'élève a été modifié avec succès.")
            else:
                # Ajout
                self.service.create_eleve(
                    matricule,
                    nom,
                    prenom,
                    date_naissance,
                    sexe,
                    classe_id,
                    tuteur,
                    telephone,
                )
                QMessageBox.information(self, "Succès", "L'élève a été ajouté avec succès.")

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
