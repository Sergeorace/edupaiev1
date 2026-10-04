"""
Exceptions personnalisées pour la couche métier.
"""


class ValidationError(Exception):
    """Exception levée lors d'une erreur de validation des données."""

    pass


class RegleMetierError(Exception):
    """Exception levée lors d'une violation d'une règle métier."""

    pass


class PaiementSuperieurAuSoldeError(RegleMetierError):
    """Exception levée quand un paiement dépasse le solde restant."""

    pass


class EntiteIntrouvableError(RegleMetierError):
    """Exception levée quand une entité n'est pas trouvée."""

    pass
