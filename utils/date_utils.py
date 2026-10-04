"""
Fonctions utilitaires pour la manipulation des dates.
"""

from datetime import date, datetime


def parse_date(date_str: str) -> date:
    """
    Parse une chaîne de caractères en date.

    Args:
        date_str: Chaîne de caractères au format JJ/MM/AAAA ou YYYY-MM-DD.

    Returns:
        Date correspondante.

    Raises:
        ValueError: Si le format n'est pas valide.
    """
    if not isinstance(date_str, str):
        raise ValueError("La date doit être une chaîne de caractères.")

    # Essayer le format JJ/MM/AAAA
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").date()
    except ValueError:
        pass

    # Essayer le format YYYY-MM-DD
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        pass

    raise ValueError(
        f"Format de date invalide : {date_str}. "
        "Formats acceptés : JJ/MM/AAAA ou YYYY-MM-DD"
    )


def get_annee_civile() -> int:
    """
    Retourne l'année civile actuelle.

    Returns:
        Année civile (ex: 2026).
    """
    return date.today().year


def extract_annee_from_recu_numero(numero: str) -> int:
    """
    Extrait l'année civile d'un numéro de reçu.

    Args:
        numero: Numéro de reçu (ex: "REC-2026-00001").

    Returns:
        Année civile (ex: 2026).

    Raises:
        ValueError: Si le format du numéro est invalide.
    """
    if not isinstance(numero, str):
        raise ValueError("Le numéro de reçu doit être une chaîne de caractères.")

    parts = numero.split("-")
    if (
        len(parts) != 3
        or parts[0] != "REC"
        or len(parts[1]) != 4
        or not parts[1].isdigit()
        or len(parts[2]) != 5
        or not parts[2].isdigit()
    ):
        raise ValueError(f"Format de numéro de reçu invalide : {numero}")

    return int(parts[1])
