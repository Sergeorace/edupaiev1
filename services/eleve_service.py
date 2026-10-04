"""
Service pour la gestion des élèves.
"""

import sqlite3
from datetime import date
from typing import List, Optional

from models.eleve import Eleve
from repositories.eleve_repository import EleveRepository
from utils.validators import (
    validate_required,
    validate_montant,
    validate_date,
    validate_telephone,
    validate_matricule,
    validate_sexe,
)
from utils.exceptions import ValidationError, RegleMetierError


class EleveService:
    """Service pour les opérations métier sur les élèves."""

    def __init__(self, conn: sqlite3.Connection):
        """
        Initialise le service avec une connexion.

        Args:
            conn: Connexion SQLite à utiliser.
        """
        self.conn = conn
        self.repository = EleveRepository(conn)

    def create_eleve(
        self,
        matricule: str,
        nom: str,
        prenom: str,
        date_naissance: date,
        sexe: str,
        classe_id: int,
        tuteur: str,
        telephone: str,
    ) -> Eleve:
        """
        Crée un nouvel élève avec validation.

        Args:
            matricule: Matricule de l'élève.
            nom: Nom de l'élève.
            prenom: Prénom de l'élève.
            date_naissance: Date de naissance.
            sexe: Sexe ('M' ou 'F').
            classe_id: ID de la classe.
            tuteur: Nom du tuteur.
            telephone: Numéro de téléphone.

        Returns:
            L'élève créé.

        Raises:
            ValidationError: Si les données sont invalides.
            RegleMetierError: Si le matricule existe déjà.
        """
        # Validation des champs
        validate_required(matricule, "matricule")
        validate_required(nom, "nom")
        validate_required(prenom, "prenom")
        validate_required(tuteur, "tuteur")
        validate_required(telephone, "téléphone")

        validate_matricule(matricule)
        validate_sexe(sexe)
        validate_date(date_naissance, allow_future=True)  # Naissance peut être dans le futur pour tests
        validate_telephone(telephone)

        # Vérifier l'unicité du matricule
        existing = self.repository.get_by_matricule(matricule)
        if existing:
            raise RegleMetierError(
                f"Le matricule '{matricule}' est déjà utilisé par un autre élève."
            )

        # Créer l'élève
        eleve = Eleve(
            id=0,  # Sera généré par la base
            matricule=matricule.upper(),
            nom=nom.upper(),
            prenom=prenom.capitalize(),
            date_naissance=date_naissance,
            sexe=sexe.upper(),
            classe_id=classe_id,
            tuteur=tuteur.capitalize(),
            telephone=telephone,
            actif=True,
        )

        return self.repository.create(eleve)

    def update_eleve(
        self,
        eleve_id: int,
        matricule: str,
        nom: str,
        prenom: str,
        date_naissance: date,
        sexe: str,
        classe_id: int,
        tuteur: str,
        telephone: str,
    ) -> Eleve:
        """
        Met à jour un élève existant avec validation.

        Args:
            eleve_id: ID de l'élève à modifier.
            matricule: Nouveau matricule.
            nom: Nouveau nom.
            prenom: Nouveau prénom.
            date_naissance: Nouvelle date de naissance.
            sexe: Nouveau sexe.
            classe_id: Nouvelle classe.
            tuteur: Nouveau tuteur.
            telephone: Nouveau téléphone.

        Returns:
            L'élève mis à jour.

        Raises:
            ValidationError: Si les données sont invalides.
            RegleMetierError: Si le matricule existe déjà pour un autre élève.
        """
        # Vérifier que l'élève existe
        eleve = self.repository.get_by_id(eleve_id)
        if not eleve:
            raise RegleMetierError(f"Élève avec ID {eleve_id} introuvable.")

        # Validation des champs
        validate_required(matricule, "matricule")
        validate_required(nom, "nom")
        validate_required(prenom, "prenom")
        validate_required(tuteur, "tuteur")
        validate_required(telephone, "téléphone")

        validate_matricule(matricule)
        validate_sexe(sexe)
        validate_date(date_naissance, allow_future=True)
        validate_telephone(telephone)

        # Vérifier l'unicité du matricule (si différent de l'actuel)
        if matricule.upper() != eleve.matricule:
            existing = self.repository.get_by_matricule(matricule)
            if existing:
                raise RegleMetierError(
                    f"Le matricule '{matricule}' est déjà utilisé par un autre élève."
                )

        # Mettre à jour l'élève
        eleve.matricule = matricule.upper()
        eleve.nom = nom.upper()
        eleve.prenom = prenom.capitalize()
        eleve.date_naissance = date_naissance
        eleve.sexe = sexe.upper()
        eleve.classe_id = classe_id
        eleve.tuteur = tuteur.capitalize()
        eleve.telephone = telephone

        self.repository.update(eleve)
        return eleve

    def archive_eleve(self, eleve_id: int) -> None:
        """
        Archive un élève (met actif = 0).

        Args:
            eleve_id: ID de l'élève à archiver.

        Raises:
            RegleMetierError: Si l'élève n'existe pas.
        """
        eleve = self.repository.get_by_id(eleve_id)
        if not eleve:
            raise RegleMetierError(f"Élève avec ID {eleve_id} introuvable.")

        self.repository.archive(eleve_id)

    def get_eleve_by_id(self, eleve_id: int) -> Optional[Eleve]:
        """
        Récupère un élève par son ID.

        Args:
            eleve_id: ID de l'élève.

        Returns:
            L'élève trouvé ou None.
        """
        return self.repository.get_by_id(eleve_id)

    def get_eleve_by_matricule(self, matricule: str) -> Optional[Eleve]:
        """
        Récupère un élève par son matricule.

        Args:
            matricule: Matricule de l'élève.

        Returns:
            L'élève trouvé ou None.
        """
        return self.repository.get_by_matricule(matricule)

    def list_eleves(self, actif_only: bool = True) -> List[Eleve]:
        """
        Liste tous les élèves.

        Args:
            actif_only: Si True, ne retourne que les élèves actifs.

        Returns:
            Liste des élèves.
        """
        return self.repository.get_all(actif_only=actif_only)

    def search_eleves(
        self,
        nom: Optional[str] = None,
        prenom: Optional[str] = None,
        matricule: Optional[str] = None,
        classe_id: Optional[int] = None,
        actif_only: bool = True,
    ) -> List[Eleve]:
        """
        Recherche des élèves selon différents critères.

        Args:
            nom: Nom de l'élève (recherche partielle).
            prenom: Prénom de l'élève (recherche partielle).
            matricule: Matricule de l'élève (recherche partielle).
            classe_id: ID de la classe.
            actif_only: Si True, ne retourne que les élèves actifs.

        Returns:
            Liste des élèves correspondant aux critères.
        """
        return self.repository.search(
            nom=nom, prenom=prenom, matricule=matricule, classe_id=classe_id, actif_only=actif_only
        )
