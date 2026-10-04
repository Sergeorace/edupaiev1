"""
Fonctions de validation des données.
"""

from datetime import date
from typing import Optional
from utils.exceptions import ValidationError


def validate_required(value: any, field_name: str) -> None:
    """
    Valide qu'un champ n'est pas vide.

    Args:
        value: Valeur à valider.
        field_name: Nom du champ pour le message d'erreur.

    Raises:
        ValidationError: Si la valeur est vide.
    """
    if value is None or (isinstance(value, str) and value.strip() == ""):
        raise ValidationError(f"Le champ '{field_name}' est obligatoire.")


def validate_montant(montant: int) -> None:
    """
    Valide qu'un montant est un entier positif.

    Args:
        montant: Montant à valider.

    Raises:
        ValidationError: Si le montant n'est pas valide.
    """
    if not isinstance(montant, int):
        raise ValidationError("Le montant doit être un entier.")
    if montant <= 0:
        raise ValidationError("Le montant doit être supérieur à 0.")


def validate_date(date_val: date, allow_future: bool = False) -> None:
    """
    Valide qu'une date est valide.

    Args:
        date_val: Date à valider.
        allow_future: Si True, les dates futures sont autorisées.

    Raises:
        ValidationError: Si la date n'est pas valide.
    """
    if not isinstance(date_val, date):
        raise ValidationError("La date doit être une date valide.")

    if not allow_future and date_val > date.today():
        raise ValidationError("La date ne peut pas être dans le futur.")


def validate_telephone(telephone: str) -> None:
    """
    Valide un numéro de téléphone.

    Args:
        telephone: Numéro de téléphone à valider.

    Raises:
        ValidationError: Si le numéro n'est pas valide.
    """
    if not telephone or not isinstance(telephone, str):
        raise ValidationError("Le numéro de téléphone est obligatoire.")

    # Vérifier que le téléphone contient uniquement des chiffres et espaces
    cleaned = telephone.replace(" ", "")
    if not cleaned.isdigit() or len(cleaned) < 8:
        raise ValidationError(
            "Le numéro de téléphone doit contenir au moins 8 chiffres."
        )


def validate_matricule(matricule: str) -> None:
    """
    Valide un matricule.

    Args:
        matricule: Matricule à valider.

    Raises:
        ValidationError: Si le matricule n'est pas valide.
    """
    if not matricule or not isinstance(matricule, str):
        raise ValidationError("Le matricule est obligatoire.")

    if len(matricule.strip()) < 3:
        raise ValidationError("Le matricule doit contenir au moins 3 caractères.")

    # Vérifier qu'il n'y a que des caractères alphanumériques
    cleaned = matricule.strip().upper()
    if not cleaned.isalnum():
        raise ValidationError(
            "Le matricule ne doit contenir que des lettres et des chiffres."
        )


def validate_sexe(sexe: str) -> None:
    """
    Valide le sexe d'un élève.

    Args:
        sexe: Sexe à valider ('M' ou 'F').

    Raises:
        ValidationError: Si le sexe n'est pas valide.
    """
    if sexe not in ("M", "F"):
        raise ValidationError("Le sexe doit être 'M' ou 'F'.")
