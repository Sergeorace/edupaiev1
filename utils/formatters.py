"""
Fonctions de formatage des données pour l'affichage.
"""

from datetime import date


def format_montant(montant: int) -> str:
    """
    Formate un montant en FCFA avec séparateur de milliers.

    Args:
        montant: Montant à formater.

    Returns:
        Montant formaté (ex: "25 000 FCFA").
    """
    # Formater avec séparateur de milliers
    montant_str = f"{montant:,}".replace(",", " ")
    return f"{montant_str} FCFA"


def format_date(date_val: date) -> str:
    """
    Formate une date au format JJ/MM/AAAA.

    Args:
        date_val: Date à formater.

    Returns:
        Date formatée (ex: "15/09/2025").
    """
    return date_val.strftime("%d/%m/%Y")


def format_statut(statut: str) -> str:
    """
    Formate un statut pour l'affichage.

    Args:
        statut: Statut à formater.

    Returns:
        Statut formaté avec la première lettre en majuscule.
    """
    return statut.capitalize()
