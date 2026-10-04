"""
Tests unitaires pour les services.
Utilise une base de données SQLite en mémoire.
"""

from datetime import date, timedelta
from pathlib import Path
import pytest

from database.database import create_connection
from repositories.eleve_repository import EleveRepository
from repositories.paiement_repository import PaiementRepository
from repositories.frais_classe_repository import FraisClasseRepository
from repositories.dashboard_repository import DashboardRepository
from models.eleve import Eleve
from models.paiement import Paiement

from services.eleve_service import EleveService
from services.paiement_service import PaiementService
from services.recu_service import RecuService
from services.dashboard_service import DashboardService

from utils.exceptions import (
    ValidationError,
    RegleMetierError,
    PaiementSuperieurAuSoldeError,
    EntiteIntrouvableError,
)


@pytest.fixture
def in_memory_db():
    """Fixture qui crée une base de données en mémoire avec le schéma et les données."""
    conn = create_connection(":memory:")

    database_dir = Path(__file__).resolve().parents[1] / "database"
    schema_path = database_dir / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        conn.executescript(schema_sql)

    seed_path = database_dir / "seed.sql"
    with open(seed_path, "r", encoding="utf-8") as f:
        seed_sql = f.read()
        conn.executescript(seed_sql)

    conn.commit()

    yield conn

    conn.close()


class TestValidators:
    """Tests pour les validateurs."""

    def test_validate_required(self):
        """Test la validation des champs obligatoires."""
        from utils.validators import validate_required

        validate_required("test", "test")  # Ne doit pas lever

        with pytest.raises(ValidationError):
            validate_required(None, "test")

        with pytest.raises(ValidationError):
            validate_required("", "test")

        with pytest.raises(ValidationError):
            validate_required("   ", "test")

    def test_validate_montant(self):
        """Test la validation des montants."""
        from utils.validators import validate_montant

        validate_montant(100)  # Ne doit pas lever

        with pytest.raises(ValidationError):
            validate_montant(0)

        with pytest.raises(ValidationError):
            validate_montant(-100)

        with pytest.raises(ValidationError):
            validate_montant("100")

    def test_validate_date(self):
        """Test la validation des dates."""
        from utils.validators import validate_date

        validate_date(date.today())  # Ne doit pas lever
        validate_date(date(2020, 1, 1), allow_future=True)  # Ne doit pas lever

        with pytest.raises(ValidationError):
            validate_date(date.today() + timedelta(days=1))

        with pytest.raises(ValidationError):
            validate_date("2025-01-01")

    def test_validate_telephone(self):
        """Test la validation des téléphones."""
        from utils.validators import validate_telephone

        validate_telephone("0707010101")  # Ne doit pas lever
        validate_telephone("07 07 01 01 01")  # Ne doit pas lever

        with pytest.raises(ValidationError):
            validate_telephone("")

        with pytest.raises(ValidationError):
            validate_telephone("123")

        with pytest.raises(ValidationError):
            validate_telephone("abc12345")


class TestFormatters:
    """Tests pour les formatters."""

    def test_format_montant(self):
        """Test le formatage des montants."""
        from utils.formatters import format_montant

        assert format_montant(25000) == "25 000 FCFA"
        assert format_montant(150000) == "150 000 FCFA"
        assert format_montant(1000000) == "1 000 000 FCFA"

    def test_format_date(self):
        """Test le formatage des dates."""
        from utils.formatters import format_date

        assert format_date(date(2025, 9, 15)) == "15/09/2025"
        assert format_date(date(2026, 1, 1)) == "01/01/2026"


class TestEleveService:
    """Tests pour EleveService."""

    def test_create_eleve_success(self, in_memory_db):
        """Test la création réussie d'un élève."""
        service = EleveService(in_memory_db)

        eleve = service.create_eleve(
            matricule="MAT999",
            nom="KOUASSI",
            prenom="Jean",
            date_naissance=date(2012, 5, 15),
            sexe="M",
            classe_id=1,
            tuteur="KOUASSI Paul",
            telephone="0707010101",
        )

        assert eleve.id > 0
        assert eleve.matricule == "MAT999"
        assert eleve.nom == "KOUASSI"
        assert eleve.prenom == "Jean"

    def test_create_eleve_duplicate_matricule(self, in_memory_db):
        """Test l'erreur de matricule en double."""
        service = EleveService(in_memory_db)

        service.create_eleve(
            matricule="MAT998",
            nom="KOUASSI",
            prenom="Jean",
            date_naissance=date(2012, 5, 15),
            sexe="M",
            classe_id=1,
            tuteur="KOUASSI Paul",
            telephone="0707010101",
        )

        with pytest.raises(RegleMetierError, match="déjà utilisé"):
            service.create_eleve(
                matricule="MAT998",
                nom="DIALLO",
                prenom="Aminata",
                date_naissance=date(2012, 8, 22),
                sexe="F",
                classe_id=1,
                tuteur="DIALLO Ibrahim",
                telephone="0707010102",
            )

    def test_create_eleve_validation_error(self, in_memory_db):
        """Test les erreurs de validation."""
        service = EleveService(in_memory_db)

        # Montant invalide (pas applicable ici, mais teste le validateur)
        # Test téléphone invalide
        with pytest.raises(ValidationError):
            service.create_eleve(
                matricule="MAT997",
                nom="KOUASSI",
                prenom="Jean",
                date_naissance=date(2012, 5, 15),
                sexe="M",
                classe_id=1,
                tuteur="KOUASSI Paul",
                telephone="123",  # Trop court
            )

        # Sexe invalide
        with pytest.raises(ValidationError):
            service.create_eleve(
                matricule="MAT996",
                nom="KOUASSI",
                prenom="Jean",
                date_naissance=date(2012, 5, 15),
                sexe="X",  # Invalide
                classe_id=1,
                tuteur="KOUASSI Paul",
                telephone="0707010101",
            )

    def test_update_eleve_success(self, in_memory_db):
        """Test la mise à jour réussie d'un élève."""
        service = EleveService(in_memory_db)

        eleve = service.create_eleve(
            matricule="MAT995",
            nom="KOUASSI",
            prenom="Jean",
            date_naissance=date(2012, 5, 15),
            sexe="M",
            classe_id=1,
            tuteur="KOUASSI Paul",
            telephone="0707010101",
        )

        updated = service.update_eleve(
            eleve_id=eleve.id,
            matricule="MAT995",
            nom="DIALLO",
            prenom="Aminata",
            date_naissance=date(2012, 8, 22),
            sexe="F",
            classe_id=2,
            tuteur="DIALLO Ibrahim",
            telephone="0707010102",
        )

        assert updated.nom == "DIALLO"
        assert updated.prenom == "Aminata"

    def test_archive_eleve(self, in_memory_db):
        """Test l'archivage d'un élève."""
        service = EleveService(in_memory_db)

        eleve = service.create_eleve(
            matricule="MAT994",
            nom="KOUASSI",
            prenom="Jean",
            date_naissance=date(2012, 5, 15),
            sexe="M",
            classe_id=1,
            tuteur="KOUASSI Paul",
            telephone="0707010101",
        )

        service.archive_eleve(eleve.id)

        archived = service.get_eleve_by_id(eleve.id)
        assert archived.actif is False


class TestPaiementService:
    """Tests pour PaiementService."""

    def test_calculer_frais_dus(self, in_memory_db):
        """Test le calcul des frais dus."""
        service = PaiementService(in_memory_db)

        # L'élève MAT001 est en 6ème A (classe_id=1)
        # Frais : 25000 + 150000 + 10000 = 185000
        frais = service.calculer_frais_dus(1, 1)

        assert frais == 185000

    def test_calculer_total_paye(self, in_memory_db):
        """Test le calcul du total payé."""
        service = PaiementService(in_memory_db)

        # MAT001 a 2 paiements valides : 50000 + 50000 = 100000
        total = service.calculer_total_paye(1, 1)

        assert total == 100000

    def test_calculer_solde(self, in_memory_db):
        """Test le calcul du solde."""
        service = PaiementService(in_memory_db)

        # MAT001 : 185000 - 100000 = 85000
        solde = service.calculer_solde(1, 1)

        assert solde == 85000

    def test_calculer_statut(self, in_memory_db):
        """Test le calcul du statut."""
        service = PaiementService(in_memory_db)

        # MAT001 : Partiel (0 < payé < dû)
        statut = service.calculer_statut(1, 1)
        assert statut == "Partiel"

        # MAT005 : Payé (solde = 0)
        statut = service.calculer_statut(5, 1)
        assert statut == "Payé"

    def test_enregistrer_paiement_success(self, in_memory_db):
        """Test l'enregistrement réussi d'un paiement."""
        service = PaiementService(in_memory_db)

        # MAT003 a un solde de 35000
        paiement = service.enregistrer_paiement(
            eleve_id=3,
            annee_id=1,
            montant=35000,
            date_paiement=date.today(),
            mode_paiement="Espèces",
            motif="Solde",
        )

        assert paiement.id > 0
        assert paiement.montant == 35000
        assert paiement.statut == "valide"

    def test_enregistrer_paiement_superieur_au_solde(self, in_memory_db):
        """Test l'erreur quand le paiement dépasse le solde."""
        service = PaiementService(in_memory_db)

        # MAT003 a un solde de 35000
        with pytest.raises(PaiementSuperieurAuSoldeError):
            service.enregistrer_paiement(
                eleve_id=3,
                annee_id=1,
                montant=50000,  # Dépasse le solde
                date_paiement=date.today(),
                mode_paiement="Espèces",
            )

    def test_enregistrer_paiement_montant_zero(self, in_memory_db):
        """Test l'erreur quand le montant est 0."""
        service = PaiementService(in_memory_db)

        with pytest.raises(ValidationError):
            service.enregistrer_paiement(
                eleve_id=1,
                annee_id=1,
                montant=0,
                date_paiement=date.today(),
                mode_paiement="Espèces",
            )

    def test_enregistrer_paiement_montant_negatif(self, in_memory_db):
        """Test l'erreur quand le montant est négatif."""
        service = PaiementService(in_memory_db)

        with pytest.raises(ValidationError):
            service.enregistrer_paiement(
                eleve_id=1,
                annee_id=1,
                montant=-1000,
                date_paiement=date.today(),
                mode_paiement="Espèces",
            )

    def test_enregistrer_paiement_date_future(self, in_memory_db):
        """Test l'erreur quand la date est dans le futur."""
        service = PaiementService(in_memory_db)

        with pytest.raises(ValidationError):
            service.enregistrer_paiement(
                eleve_id=1,
                annee_id=1,
                montant=50000,
                date_paiement=date.today() + timedelta(days=1),
                mode_paiement="Espèces",
            )

    def test_annuler_paiement_success(self, in_memory_db):
        """Test l'annulation réussie d'un paiement."""
        service = PaiementService(in_memory_db)

        # Créer un nouveau paiement pour l'annuler
        paiement = service.enregistrer_paiement(
            eleve_id=3,
            annee_id=1,
            montant=10000,
            date_paiement=date.today(),
            mode_paiement="Espèces",
        )

        service.annuler_paiement(paiement.id, "Test d'annulation")

        annule = service.paiement_repo.get_by_id(paiement.id)
        assert annule.statut == "annule"
        assert annule.motif_annulation == "Test d'annulation"

    def test_annuler_paiement_sans_motif(self, in_memory_db):
        """Test l'erreur quand le motif d'annulation est vide."""
        service = PaiementService(in_memory_db)

        paiement = service.enregistrer_paiement(
            eleve_id=3,
            annee_id=1,
            montant=10000,
            date_paiement=date.today(),
            mode_paiement="Espèces",
        )

        with pytest.raises(ValidationError):
            service.annuler_paiement(paiement.id, "")

    def test_annuler_paiement_deja_annule(self, in_memory_db):
        """Test l'erreur quand le paiement est déjà annulé."""
        service = PaiementService(in_memory_db)

        paiement = service.enregistrer_paiement(
            eleve_id=3,
            annee_id=1,
            montant=10000,
            date_paiement=date.today(),
            mode_paiement="Espèces",
        )

        service.annuler_paiement(paiement.id, "Première annulation")

        with pytest.raises(RegleMetierError, match="déjà annulé"):
            service.annuler_paiement(paiement.id, "Seconde annulation")


class TestRecuService:
    """Tests pour RecuService."""

    def test_get_recu_by_numero(self, in_memory_db):
        """Test la récupération d'un reçu par numéro."""
        service = RecuService(in_memory_db)

        recu = service.get_recu_by_numero("REC-2026-00001")

        assert recu is not None
        assert recu.numero == "REC-2026-00001"

    def test_get_recu_by_paiement(self, in_memory_db):
        """Test la récupération d'un reçu par paiement."""
        service = RecuService(in_memory_db)

        # Le paiement 1 a un reçu
        recu = service.get_recu_by_paiement(1)

        assert recu is not None
        assert recu.paiement_id == 1

    def test_generer_numero_recu(self, in_memory_db):
        """Test la génération d'un numéro de reçu."""
        service = RecuService(in_memory_db)

        numero = service.generer_numero_recu(1)

        assert numero.startswith("REC-")
        assert len(numero.split("-")) == 3


class TestDashboardService:
    """Tests pour DashboardService."""

    def test_get_total_encaisse(self, in_memory_db):
        """Test le calcul du total encaissé."""
        service = DashboardService(in_memory_db)

        total = service.get_total_encaisse(1)

        assert total > 0
        assert isinstance(total, int)

    def test_get_total_restant_du(self, in_memory_db):
        """Test le calcul du total restant dû."""
        service = DashboardService(in_memory_db)

        total = service.get_total_restant_du(1)

        assert total >= 0
        assert isinstance(total, int)

    def test_get_nombre_eleves_par_statut(self, in_memory_db):
        """Test le comptage d'élèves par statut."""
        service = DashboardService(in_memory_db)

        stats = service.get_nombre_eleves_par_statut(1)

        assert "Impayé" in stats
        assert "Partiel" in stats
        assert "Payé" in stats
        assert isinstance(stats["Impayé"], int)
        assert isinstance(stats["Partiel"], int)
        assert isinstance(stats["Payé"], int)

    def test_get_derniers_paiements(self, in_memory_db):
        """Test la récupération des derniers paiements."""
        service = DashboardService(in_memory_db)

        paiements = service.get_derniers_paiements(1, limit=5)

        assert len(paiements) <= 5
        assert isinstance(paiements, list)
        if paiements:
            assert "montant" in paiements[0]
            assert "eleve_nom" in paiements[0]
