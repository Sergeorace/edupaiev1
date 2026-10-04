"""
Tests unitaires pour les repositories.
Utilise une base de données SQLite en mémoire.
"""

import sqlite3
from datetime import date
import pytest

from database.database import create_connection, get_transaction
from repositories.eleve_repository import EleveRepository
from repositories.paiement_repository import PaiementRepository
from repositories.recu_repository import RecuRepository
from models.eleve import Eleve
from models.paiement import Paiement
from models.recu import Recu


@pytest.fixture
def in_memory_db():
    """Fixture qui crée une base de données en mémoire avec le schéma."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    # Création du schéma
    schema_path = "database/schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        conn.executescript(schema_sql)

    # Insertion des données de test minimales
    conn.execute(
        "INSERT INTO annees_scolaires (annee, date_debut, date_fin) VALUES (?, ?, ?)",
        ("2025-2026", "2025-09-01", "2026-07-31"),
    )
    conn.execute(
        "INSERT INTO classes (nom, niveau) VALUES (?, ?)", ("6ème A", "Collège")
    )
    conn.execute(
        "INSERT INTO frais_classe (classe_id, annee_id, type_frais, montant, description) VALUES (?, ?, ?, ?, ?)",
        (1, 1, "Inscription", 25000, "Frais d'inscription"),
    )
    conn.execute(
        "INSERT INTO frais_classe (classe_id, annee_id, type_frais, montant, description) VALUES (?, ?, ?, ?, ?)",
        (1, 1, "Scolarité", 150000, "Frais de scolarité"),
    )
    conn.commit()

    yield conn

    conn.close()


class TestEleveRepository:
    """Tests pour EleveRepository."""

    def test_create_eleve(self, in_memory_db):
        """Test la création d'un élève."""
        repo = EleveRepository(in_memory_db)
        eleve = Eleve(
            id=0,
            matricule="MAT999",
            nom="TEST",
            prenom="Test",
            date_naissance=date(2012, 1, 1),
            sexe="M",
            classe_id=1,
            tuteur="Test Tuteur",
            telephone="0123456789",
            actif=True,
        )

        created = repo.create(eleve)

        assert created.id > 0
        assert created.matricule == "MAT999"

    def test_get_by_id(self, in_memory_db):
        """Test la récupération d'un élève par ID."""
        repo = EleveRepository(in_memory_db)
        eleve = Eleve(
            id=0,
            matricule="MAT998",
            nom="TEST",
            prenom="Test",
            date_naissance=date(2012, 1, 1),
            sexe="M",
            classe_id=1,
            tuteur="Test Tuteur",
            telephone="0123456789",
            actif=True,
        )
        created = repo.create(eleve)

        found = repo.get_by_id(created.id)

        assert found is not None
        assert found.matricule == "MAT998"

    def test_get_by_matricule(self, in_memory_db):
        """Test la récupération d'un élève par matricule."""
        repo = EleveRepository(in_memory_db)
        eleve = Eleve(
            id=0,
            matricule="MAT997",
            nom="TEST",
            prenom="Test",
            date_naissance=date(2012, 1, 1),
            sexe="M",
            classe_id=1,
            tuteur="Test Tuteur",
            telephone="0123456789",
            actif=True,
        )
        repo.create(eleve)

        found = repo.get_by_matricule("MAT997")

        assert found is not None
        assert found.nom == "TEST"

    def test_get_all(self, in_memory_db):
        """Test la récupération de tous les élèves."""
        repo = EleveRepository(in_memory_db)
        eleve1 = Eleve(
            id=0,
            matricule="MAT001",
            nom="A",
            prenom="Test",
            date_naissance=date(2012, 1, 1),
            sexe="M",
            classe_id=1,
            tuteur="Tuteur",
            telephone="0123456789",
            actif=True,
        )
        eleve2 = Eleve(
            id=0,
            matricule="MAT002",
            nom="B",
            prenom="Test",
            date_naissance=date(2012, 1, 1),
            sexe="F",
            classe_id=1,
            tuteur="Tuteur",
            telephone="0123456789",
            actif=True,
        )
        repo.create(eleve1)
        repo.create(eleve2)

        all_eleves = repo.get_all()

        assert len(all_eleves) == 2

    def test_search(self, in_memory_db):
        """Test la recherche d'élèves."""
        repo = EleveRepository(in_memory_db)
        eleve = Eleve(
            id=0,
            matricule="MAT996",
            nom="KOUASSI",
            prenom="Jean",
            date_naissance=date(2012, 1, 1),
            sexe="M",
            classe_id=1,
            tuteur="Tuteur",
            telephone="0123456789",
            actif=True,
        )
        repo.create(eleve)

        results = repo.search(nom="KOUA")

        assert len(results) == 1
        assert results[0].nom == "KOUASSI"

    def test_archive(self, in_memory_db):
        """Test l'archivage d'un élève."""
        repo = EleveRepository(in_memory_db)
        eleve = Eleve(
            id=0,
            matricule="MAT995",
            nom="TEST",
            prenom="Test",
            date_naissance=date(2012, 1, 1),
            sexe="M",
            classe_id=1,
            tuteur="Tuteur",
            telephone="0123456789",
            actif=True,
        )
        created = repo.create(eleve)

        repo.archive(created.id)

        archived = repo.get_by_id(created.id)
        assert archived.actif is False

    def test_update(self, in_memory_db):
        """Test la mise à jour d'un élève."""
        repo = EleveRepository(in_memory_db)
        eleve = Eleve(
            id=0,
            matricule="MAT994",
            nom="TEST",
            prenom="Test",
            date_naissance=date(2012, 1, 1),
            sexe="M",
            classe_id=1,
            tuteur="Tuteur",
            telephone="0123456789",
            actif=True,
        )
        created = repo.create(eleve)
        created.nom = "MODIFIED"

        repo.update(created)

        updated = repo.get_by_id(created.id)
        assert updated.nom == "MODIFIED"


class TestPaiementRepository:
    """Tests pour PaiementRepository."""

    def test_create_paiement(self, in_memory_db):
        """Test la création d'un paiement."""
        # D'abord créer un élève
        eleve_repo = EleveRepository(in_memory_db)
        eleve = Eleve(
            id=0,
            matricule="MAT993",
            nom="TEST",
            prenom="Test",
            date_naissance=date(2012, 1, 1),
            sexe="M",
            classe_id=1,
            tuteur="Tuteur",
            telephone="0123456789",
            actif=True,
        )
        created_eleve = eleve_repo.create(eleve)

        # Créer le paiement
        paiement_repo = PaiementRepository(in_memory_db)
        paiement = Paiement(
            id=0,
            eleve_id=created_eleve.id,
            annee_id=1,
            montant=50000,
            date_paiement=date(2025, 9, 15),
            mode_paiement="Espèces",
            motif="Test",
            statut="valide",
        )

        created = paiement_repo.create(paiement)

        assert created.id > 0
        assert created.montant == 50000

    def test_get_by_eleve(self, in_memory_db):
        """Test la récupération des paiements d'un élève."""
        eleve_repo = EleveRepository(in_memory_db)
        eleve = Eleve(
            id=0,
            matricule="MAT992",
            nom="TEST",
            prenom="Test",
            date_naissance=date(2012, 1, 1),
            sexe="M",
            classe_id=1,
            tuteur="Tuteur",
            telephone="0123456789",
            actif=True,
        )
        created_eleve = eleve_repo.create(eleve)

        paiement_repo = PaiementRepository(in_memory_db)
        paiement1 = Paiement(
            id=0,
            eleve_id=created_eleve.id,
            annee_id=1,
            montant=50000,
            date_paiement=date(2025, 9, 15),
            mode_paiement="Espèces",
            statut="valide",
        )
        paiement2 = Paiement(
            id=0,
            eleve_id=created_eleve.id,
            annee_id=1,
            montant=25000,
            date_paiement=date(2025, 10, 15),
            mode_paiement="Espèces",
            statut="valide",
        )
        paiement_repo.create(paiement1)
        paiement_repo.create(paiement2)

        paiements = paiement_repo.get_by_eleve(created_eleve.id)

        assert len(paiements) == 2

    def test_get_valid_sum(self, in_memory_db):
        """Test le calcul de la somme des paiements valides."""
        eleve_repo = EleveRepository(in_memory_db)
        eleve = Eleve(
            id=0,
            matricule="MAT991",
            nom="TEST",
            prenom="Test",
            date_naissance=date(2012, 1, 1),
            sexe="M",
            classe_id=1,
            tuteur="Tuteur",
            telephone="0123456789",
            actif=True,
        )
        created_eleve = eleve_repo.create(eleve)

        paiement_repo = PaiementRepository(in_memory_db)
        paiement1 = Paiement(
            id=0,
            eleve_id=created_eleve.id,
            annee_id=1,
            montant=50000,
            date_paiement=date(2025, 9, 15),
            mode_paiement="Espèces",
            statut="valide",
        )
        paiement2 = Paiement(
            id=0,
            eleve_id=created_eleve.id,
            annee_id=1,
            montant=25000,
            date_paiement=date(2025, 10, 15),
            mode_paiement="Espèces",
            statut="valide",
        )
        paiement3 = Paiement(
            id=0,
            eleve_id=created_eleve.id,
            annee_id=1,
            montant=10000,
            date_paiement=date(2025, 11, 15),
            mode_paiement="Espèces",
            statut="annule",
        )
        paiement_repo.create(paiement1)
        paiement_repo.create(paiement2)
        paiement_repo.create(paiement3)

        total = paiement_repo.get_valid_sum(created_eleve.id)

        assert total == 75000  # Seuls les paiements valides

    def test_annuler(self, in_memory_db):
        """Test l'annulation d'un paiement."""
        eleve_repo = EleveRepository(in_memory_db)
        eleve = Eleve(
            id=0,
            matricule="MAT990",
            nom="TEST",
            prenom="Test",
            date_naissance=date(2012, 1, 1),
            sexe="M",
            classe_id=1,
            tuteur="Tuteur",
            telephone="0123456789",
            actif=True,
        )
        created_eleve = eleve_repo.create(eleve)

        paiement_repo = PaiementRepository(in_memory_db)
        paiement = Paiement(
            id=0,
            eleve_id=created_eleve.id,
            annee_id=1,
            montant=50000,
            date_paiement=date(2025, 9, 15),
            mode_paiement="Espèces",
            statut="valide",
        )
        created = paiement_repo.create(paiement)

        paiement_repo.annuler(created.id, "Test d'annulation")

        updated = paiement_repo.get_by_id(created.id)
        assert updated.statut == "annule"
        assert updated.motif_annulation == "Test d'annulation"


class TestRecuRepository:
    """Tests pour RecuRepository."""

    def test_create_recu(self, in_memory_db):
        """Test la création d'un reçu."""
        # Créer un élève et un paiement d'abord
        eleve_repo = EleveRepository(in_memory_db)
        eleve = Eleve(
            id=0,
            matricule="MAT989",
            nom="TEST",
            prenom="Test",
            date_naissance=date(2012, 1, 1),
            sexe="M",
            classe_id=1,
            tuteur="Tuteur",
            telephone="0123456789",
            actif=True,
        )
        created_eleve = eleve_repo.create(eleve)

        paiement_repo = PaiementRepository(in_memory_db)
        paiement = Paiement(
            id=0,
            eleve_id=created_eleve.id,
            annee_id=1,
            montant=50000,
            date_paiement=date(2025, 9, 15),
            mode_paiement="Espèces",
            statut="valide",
        )
        created_paiement = paiement_repo.create(paiement)

        # Créer le reçu
        recu_repo = RecuRepository(in_memory_db)
        recu = Recu(
            id=0,
            numero="REC-2026-00001",
            paiement_id=created_paiement.id,
            annee_id=1,
            donnees_json='{"test": "data"}',
        )

        created = recu_repo.create(recu)

        assert created.id > 0
        assert created.numero == "REC-2026-00001"

    def test_get_by_numero(self, in_memory_db):
        """Test la récupération d'un reçu par numéro."""
        # Créer un élève et un paiement d'abord
        eleve_repo = EleveRepository(in_memory_db)
        eleve = Eleve(
            id=0,
            matricule="MAT988",
            nom="TEST",
            prenom="Test",
            date_naissance=date(2012, 1, 1),
            sexe="M",
            classe_id=1,
            tuteur="Tuteur",
            telephone="0123456789",
            actif=True,
        )
        created_eleve = eleve_repo.create(eleve)

        paiement_repo = PaiementRepository(in_memory_db)
        paiement = Paiement(
            id=0,
            eleve_id=created_eleve.id,
            annee_id=1,
            montant=50000,
            date_paiement=date(2025, 9, 15),
            mode_paiement="Espèces",
            statut="valide",
        )
        created_paiement = paiement_repo.create(paiement)

        # Créer le reçu
        recu_repo = RecuRepository(in_memory_db)
        recu = Recu(
            id=0,
            numero="REC-2026-00002",
            paiement_id=created_paiement.id,
            annee_id=1,
            donnees_json='{"test": "data"}',
        )
        recu_repo.create(recu)

        found = recu_repo.get_by_numero("REC-2026-00002")

        assert found is not None
        assert found.numero == "REC-2026-00002"

    def test_get_by_paiement(self, in_memory_db):
        """Test la récupération d'un reçu par paiement."""
        # Créer un élève et un paiement d'abord
        eleve_repo = EleveRepository(in_memory_db)
        eleve = Eleve(
            id=0,
            matricule="MAT987",
            nom="TEST",
            prenom="Test",
            date_naissance=date(2012, 1, 1),
            sexe="M",
            classe_id=1,
            tuteur="Tuteur",
            telephone="0123456789",
            actif=True,
        )
        created_eleve = eleve_repo.create(eleve)

        paiement_repo = PaiementRepository(in_memory_db)
        paiement = Paiement(
            id=0,
            eleve_id=created_eleve.id,
            annee_id=1,
            montant=50000,
            date_paiement=date(2025, 9, 15),
            mode_paiement="Espèces",
            statut="valide",
        )
        created_paiement = paiement_repo.create(paiement)

        # Créer le reçu
        recu_repo = RecuRepository(in_memory_db)
        recu = Recu(
            id=0,
            numero="REC-2026-00003",
            paiement_id=created_paiement.id,
            annee_id=1,
            donnees_json='{"test": "data"}',
        )
        recu_repo.create(recu)

        found = recu_repo.get_by_paiement(created_paiement.id)

        assert found is not None
        assert found.numero == "REC-2026-00003"

    def test_get_last_numero(self, in_memory_db):
        """Test la récupération du dernier numéro de reçu."""
        # Créer deux élèves et deux paiements
        eleve_repo = EleveRepository(in_memory_db)
        eleve1 = Eleve(
            id=0,
            matricule="MAT986",
            nom="TEST",
            prenom="Test",
            date_naissance=date(2012, 1, 1),
            sexe="M",
            classe_id=1,
            tuteur="Tuteur",
            telephone="0123456789",
            actif=True,
        )
        eleve2 = Eleve(
            id=0,
            matricule="MAT985",
            nom="TEST",
            prenom="Test",
            date_naissance=date(2012, 1, 1),
            sexe="M",
            classe_id=1,
            tuteur="Tuteur",
            telephone="0123456789",
            actif=True,
        )
        created_eleve1 = eleve_repo.create(eleve1)
        created_eleve2 = eleve_repo.create(eleve2)

        paiement_repo = PaiementRepository(in_memory_db)
        paiement1 = Paiement(
            id=0,
            eleve_id=created_eleve1.id,
            annee_id=1,
            montant=50000,
            date_paiement=date(2025, 9, 15),
            mode_paiement="Espèces",
            statut="valide",
        )
        paiement2 = Paiement(
            id=0,
            eleve_id=created_eleve2.id,
            annee_id=1,
            montant=50000,
            date_paiement=date(2025, 9, 15),
            mode_paiement="Espèces",
            statut="valide",
        )
        created_paiement1 = paiement_repo.create(paiement1)
        created_paiement2 = paiement_repo.create(paiement2)

        # Créer les reçus
        recu_repo = RecuRepository(in_memory_db)
        recu1 = Recu(
            id=0,
            numero="REC-2026-00001",
            paiement_id=created_paiement1.id,
            annee_id=1,
            donnees_json='{"test": "data"}',
        )
        recu2 = Recu(
            id=0,
            numero="REC-2026-00005",
            paiement_id=created_paiement2.id,
            annee_id=1,
            donnees_json='{"test": "data"}',
        )
        recu_repo.create(recu1)
        recu_repo.create(recu2)

        last = recu_repo.get_last_numero(1)

        assert last == "REC-2026-00005"

    def test_get_donnees(self, in_memory_db):
        """Test l'extraction des données JSON d'un reçu."""
        # Créer un élève et un paiement d'abord
        eleve_repo = EleveRepository(in_memory_db)
        eleve = Eleve(
            id=0,
            matricule="MAT984",
            nom="TEST",
            prenom="Test",
            date_naissance=date(2012, 1, 1),
            sexe="M",
            classe_id=1,
            tuteur="Tuteur",
            telephone="0123456789",
            actif=True,
        )
        created_eleve = eleve_repo.create(eleve)

        paiement_repo = PaiementRepository(in_memory_db)
        paiement = Paiement(
            id=0,
            eleve_id=created_eleve.id,
            annee_id=1,
            montant=50000,
            date_paiement=date(2025, 9, 15),
            mode_paiement="Espèces",
            statut="valide",
        )
        created_paiement = paiement_repo.create(paiement)

        # Créer le reçu
        recu_repo = RecuRepository(in_memory_db)
        recu = Recu(
            id=0,
            numero="REC-2026-00004",
            paiement_id=created_paiement.id,
            annee_id=1,
            donnees_json='{"nom": "Test", "montant": 50000}',
        )
        created = recu_repo.create(recu)

        donnees = created.get_donnees()

        assert donnees["nom"] == "Test"
        assert donnees["montant"] == 50000
