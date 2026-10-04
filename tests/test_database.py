"""Tests d'initialisation et de transaction de la base SQLite."""

from datetime import date
from pathlib import Path

import pytest

from database.database import create_connection, get_transaction, init_database
from models.eleve import Eleve
from repositories.eleve_repository import EleveRepository
from repositories.paiement_repository import PaiementRepository
from repositories.recu_repository import RecuRepository


def test_init_database_seed_is_idempotent(tmp_path):
    """Vérifie que la génération répétée conserve un jeu de test unique."""
    database_path = tmp_path / "school.db"

    init_database(database_path)
    init_database(database_path)

    conn = create_connection(database_path)
    try:
        eleve_repo = EleveRepository(conn)
        paiement_repo = PaiementRepository(conn)
        recu_repo = RecuRepository(conn)

        assert len(eleve_repo.get_all(actif_only=False)) == 20
        assert sum(
            len(paiement_repo.get_by_eleve(eleve.id))
            for eleve in eleve_repo.get_all(actif_only=False)
        ) == 37
        assert len(recu_repo.get_by_annee(1)) == 37
    finally:
        conn.close()


def test_transaction_rolls_back_repository_changes():
    """Vérifie qu'une exception annule les changements des repositories."""
    conn = create_connection(":memory:")
    try:
        database_dir = Path(__file__).resolve().parents[1] / "database"
        schema_path = database_dir / "schema.sql"
        test_seed_path = database_dir / "test_seed.sql"
        conn.executescript(schema_path.read_text(encoding="utf-8"))
        conn.executescript(test_seed_path.read_text(encoding="utf-8"))

        repo = EleveRepository(conn)
        eleve = Eleve(
            id=0,
            matricule="MAT-ROLLBACK",
            nom="TEST",
            prenom="Transaction",
            date_naissance=date(2012, 1, 1),
            sexe="M",
            classe_id=1,
            tuteur="Tuteur",
            telephone="0700000000",
        )

        with pytest.raises(RuntimeError, match="annuler la transaction"):
            with get_transaction(conn):
                repo.create(eleve)
                raise RuntimeError("annuler la transaction")

        assert repo.get_by_matricule("MAT-ROLLBACK") is None
    finally:
        conn.close()
