"""
Service pour la gestion des paiements.
"""

import sqlite3
import json
from datetime import date
from typing import Optional, Dict, Any

from models.paiement import Paiement
from models.eleve import Eleve
from repositories.paiement_repository import PaiementRepository
from repositories.eleve_repository import EleveRepository
from repositories.frais_classe_repository import FraisClasseRepository
from database.database import get_transaction
from utils.validators import validate_required, validate_montant, validate_date
from utils.exceptions import (
    ValidationError,
    RegleMetierError,
    PaiementSuperieurAuSoldeError,
    EntiteIntrouvableError,
)


class PaiementService:
    """Service pour les opérations métier sur les paiements."""

    def __init__(self, conn: sqlite3.Connection):
        """
        Initialise le service avec une connexion.

        Args:
            conn: Connexion SQLite à utiliser.
        """
        self.conn = conn
        self.paiement_repo = PaiementRepository(conn)
        self.eleve_repo = EleveRepository(conn)
        self.frais_repo = FraisClasseRepository(conn)

    def calculer_frais_dus(self, eleve_id: int, annee_id: int) -> int:
        """
        Calcule les frais dus par un élève pour une année scolaire.

        Args:
            eleve_id: ID de l'élève.
            annee_id: ID de l'année scolaire.

        Returns:
            Somme des frais dus.

        Raises:
            EntiteIntrouvableError: Si l'élève n'existe pas.
        """
        eleve = self.eleve_repo.get_by_id(eleve_id)
        if not eleve:
            raise EntiteIntrouvableError(f"Élève avec ID {eleve_id} introuvable.")

        return self.frais_repo.get_total_by_classe_and_annee(eleve.classe_id, annee_id)

    def calculer_total_paye(self, eleve_id: int, annee_id: int) -> int:
        """
        Calcule le total des paiements valides d'un élève pour une année.

        Args:
            eleve_id: ID de l'élève.
            annee_id: ID de l'année scolaire.

        Returns:
            Somme des paiements valides.
        """
        return self.paiement_repo.get_valid_sum(eleve_id, annee_id)

    def calculer_solde(self, eleve_id: int, annee_id: int) -> int:
        """
        Calcule le solde restant d'un élève pour une année.

        Args:
            eleve_id: ID de l'élève.
            annee_id: ID de l'année scolaire.

        Returns:
            Solde restant (frais dus - total payé).
        """
        frais_dus = self.calculer_frais_dus(eleve_id, annee_id)
        total_paye = self.calculer_total_paye(eleve_id, annee_id)
        return frais_dus - total_paye

    def calculer_statut(self, eleve_id: int, annee_id: int) -> str:
        """
        Calcule le statut de paiement d'un élève.

        Args:
            eleve_id: ID de l'élève.
            annee_id: ID de l'année scolaire.

        Returns:
            Statut : "Impayé", "Partiel" ou "Payé".
        """
        total_paye = self.calculer_total_paye(eleve_id, annee_id)
        solde = self.calculer_solde(eleve_id, annee_id)

        if total_paye == 0:
            return "Impayé"
        elif solde == 0:
            return "Payé"
        else:
            return "Partiel"

    def enregistrer_paiement(
        self,
        eleve_id: int,
        annee_id: int,
        montant: int,
        date_paiement: date,
        mode_paiement: str,
        motif: Optional[str] = None,
    ) -> Paiement:
        """
        Enregistre un paiement dans une transaction unique.

        Args:
            eleve_id: ID de l'élève.
            annee_id: ID de l'année scolaire.
            montant: Montant du paiement.
            date_paiement: Date du paiement.
            mode_paiement: Mode de paiement ("Espèces", "Chèque", "Virement", "Mobile").
            motif: Motif optionnel du paiement.

        Returns:
            Le paiement enregistré.

        Raises:
            ValidationError: Si les données sont invalides.
            EntiteIntrouvableError: Si l'élève n'existe pas.
            PaiementSuperieurAuSoldeError: Si le paiement dépasse le solde restant.
        """
        # Validation des champs
        validate_required(montant, "montant")
        validate_required(date_paiement, "date de paiement")
        validate_required(mode_paiement, "mode de paiement")

        validate_montant(montant)
        validate_date(date_paiement, allow_future=False)

        if mode_paiement not in ("Espèces", "Chèque", "Virement", "Mobile"):
            raise ValidationError(
                "Le mode de paiement doit être 'Espèces', 'Chèque', 'Virement' ou 'Mobile'."
            )

        # Vérifier que l'élève existe
        eleve = self.eleve_repo.get_by_id(eleve_id)
        if not eleve:
            raise EntiteIntrouvableError(f"Élève avec ID {eleve_id} introuvable.")

        # Calculer le solde restant
        solde_restant = self.calculer_solde(eleve_id, annee_id)

        # Vérifier que le paiement ne dépasse pas le solde
        if montant > solde_restant:
            raise PaiementSuperieurAuSoldeError(
                f"Le paiement de {montant} FCFA dépasse le solde restant de {solde_restant} FCFA."
            )

        # Transaction : insertion du paiement + génération du reçu
        with get_transaction(self.conn) as cursor:
            # 1. Insérer le paiement
            paiement = Paiement(
                id=0,
                eleve_id=eleve_id,
                annee_id=annee_id,
                montant=montant,
                date_paiement=date_paiement,
                mode_paiement=mode_paiement,
                motif=motif,
                statut="valide",
            )
            paiement = self.paiement_repo.create(paiement)

            # 2. Préparer les données figées du reçu
            total_paye_apres = self.calculer_total_paye(eleve_id, annee_id)
            solde_apres = self.calculer_solde(eleve_id, annee_id)

            donnees_recu = {
                "nom": eleve.nom_complet,
                "classe": eleve.classe_nom or f"Classe {eleve.classe_id}",
                "montant": montant,
                "total_paye": total_paye_apres,
                "solde": solde_apres,
                "date_paiement": date_paiement.isoformat(),
            }

            # 3. Générer le numéro de reçu
            numero_recu = self._generer_numero_recu(annee_id)

            # 4. Insérer le reçu
            from models.recu import Recu
            from repositories.recu_repository import RecuRepository

            recu_repo = RecuRepository(self.conn)
            recu = Recu(
                id=0,
                numero=numero_recu,
                paiement_id=paiement.id,
                annee_id=annee_id,
                donnees_json=json.dumps(donnees_recu),
            )
            recu_repo.create(recu)

        return paiement

    def annuler_paiement(self, paiement_id: int, motif_annulation: str) -> None:
        """
        Annule un paiement avec motif obligatoire.

        Args:
            paiement_id: ID du paiement à annuler.
            motif_annulation: Motif de l'annulation.

        Raises:
            ValidationError: Si le motif est vide.
            EntiteIntrouvableError: Si le paiement n'existe pas.
            RegleMetierError: Si le paiement est déjà annulé.
        """
        validate_required(motif_annulation, "motif d'annulation")

        # Vérifier que le paiement existe
        paiement = self.paiement_repo.get_by_id(paiement_id)
        if not paiement:
            raise EntiteIntrouvableError(f"Paiement avec ID {paiement_id} introuvable.")

        # Vérifier que le paiement n'est pas déjà annulé
        if paiement.statut == "annule":
            raise RegleMetierError("Ce paiement est déjà annulé.")

        # Annuler le paiement
        self.paiement_repo.annuler(paiement_id, motif_annulation)

    def get_paiements_eleve(self, eleve_id: int, annee_id: int) -> List[Paiement]:
        """
        Récupère tous les paiements d'un élève pour une année.

        Args:
            eleve_id: ID de l'élève.
            annee_id: ID de l'année scolaire.

        Returns:
            Liste des paiements.
        """
        return self.paiement_repo.get_by_eleve(eleve_id, annee_id)

    def get_paiement_by_id(self, paiement_id: int) -> Optional[Paiement]:
        """
        Récupère un paiement par son ID.

        Args:
            paiement_id: ID du paiement.

        Returns:
            Le paiement trouvé ou None.
        """
        return self.paiement_repo.get_by_id(paiement_id)

    def _generer_numero_recu(self, annee_id: int) -> str:
        """
        Génère un numéro de reçu unique pour une année.

        Args:
            annee_id: ID de l'année scolaire.

        Returns:
            Numéro de reçu au format REC-AAAA-NNNNN.
        """
        from repositories.recu_repository import RecuRepository
        from utils.date_utils import get_annee_civile

        recu_repo = RecuRepository(self.conn)
        last_numero = recu_repo.get_last_numero(annee_id)

        annee_civile = get_annee_civile()

        if last_numero:
            # Extraire le numéro séquentiel et l'incrémenter
            last_seq = int(last_numero.split("-")[2])
            new_seq = last_seq + 1
        else:
            new_seq = 1

        return f"REC-{annee_civile}-{new_seq:05d}"
