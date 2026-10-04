"""Outils communs pour présenter les erreurs des appels de services."""

import logging
from collections.abc import Callable
from typing import TypeVar

from PySide6.QtWidgets import QMessageBox, QWidget

from utils.exceptions import RegleMetierError, ValidationError

_T = TypeVar("_T")
_LOGGER = logging.getLogger("gestion_scolarite.ui")


def run_service_operation(
    parent: QWidget,
    operation: str,
    callback: Callable[[], _T],
) -> tuple[bool, _T | None]:
    """Exécute un appel de service et présente ses erreurs à l'utilisateur."""
    try:
        return True, callback()
    except (ValidationError, RegleMetierError) as error:
        QMessageBox.warning(parent, "Vérification nécessaire", str(error))
    except Exception:
        _LOGGER.exception("Erreur inattendue pendant l'opération : %s", operation)
        QMessageBox.critical(
            parent,
            "Erreur",
            f"Une erreur inattendue s'est produite pendant {operation}. "
            "Les détails ont été enregistrés dans le journal.",
        )
    return False, None
