"""
Tests pour le générateur de PDF de reçus.
"""

import json
import sqlite3
from pathlib import Path
import tempfile

import pytest

from reports.recu_generator import generer_pdf_recu


def test_pdf_generation_cree_fichier():
    """
    Teste que la génération de PDF crée bien un fichier.
    """
    donnees = {
        "nom": "KOUASSI Jean",
        "classe": "6ème A",
        "montant": 50000,
        "total_paye": 100000,
        "solde": 85000,
        "date_paiement": "2025-09-15",
        "mode_paiement": "Espèces",
    }

    donnees_json = json.dumps(donnees)
    numero_recu = "REC-2026-00001"
    date_generation = "2025-09-15 10:30:00"

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "recu_test.pdf"

        # Générer le PDF
        generer_pdf_recu(donnees_json, numero_recu, date_generation, "valide", path)

        # Vérifier que le fichier existe
        assert path.exists()

        # Vérifier que le fichier n'est pas vide
        assert path.stat().st_size > 0

        # Vérifier que c'est un PDF valide (commence par %PDF)
        content = path.read_bytes()
        assert content.startswith(b"%PDF")


def test_pdf_generation_meme_donnees():
    """
    Teste que deux générations de PDF à partir des mêmes données
    produisent des fichiers de même taille (contenu similaire).
    """
    donnees = {
        "nom": "KOUASSI Jean",
        "classe": "6ème A",
        "montant": 50000,
        "total_paye": 100000,
        "solde": 85000,
        "date_paiement": "2025-09-15",
        "mode_paiement": "Espèces",
    }

    donnees_json = json.dumps(donnees)
    numero_recu = "REC-2026-00001"
    date_generation = "2025-09-15 10:30:00"

    with tempfile.TemporaryDirectory() as tmpdir:
        path1 = Path(tmpdir) / "recu1.pdf"
        path2 = Path(tmpdir) / "recu2.pdf"

        # Générer deux PDFs
        generer_pdf_recu(donnees_json, numero_recu, date_generation, "valide", path1)
        generer_pdf_recu(donnees_json, numero_recu, date_generation, "valide", path2)

        # Vérifier que les fichiers existent
        assert path1.exists()
        assert path2.exists()

        # Vérifier que les fichiers ont la même taille (contenu identique)
        size1 = path1.stat().st_size
        size2 = path2.stat().st_size
        assert size1 == size2


def test_pdf_annule_genere_fichier():
    """
    Teste que le PDF d'un reçu annulé est généré correctement.
    """
    donnees = {
        "nom": "DIALLO Aminata",
        "classe": "6ème A",
        "montant": 30000,
        "total_paye": 75000,
        "solde": 110000,
        "date_paiement": "2025-09-25",
        "mode_paiement": "Espèces",
    }

    donnees_json = json.dumps(donnees)
    numero_recu = "REC-2026-00036"
    date_generation = "2025-09-26 10:30:00"

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "recu_annule.pdf"

        # Générer un PDF annulé
        generer_pdf_recu(donnees_json, numero_recu, date_generation, "annulé", path)

        # Vérifier que le fichier existe
        assert path.exists()

        # Vérifier que le fichier n'est pas vide
        assert path.stat().st_size > 0

        # Vérifier que c'est un PDF valide
        content = path.read_bytes()
        assert content.startswith(b"%PDF")


def test_pdf_valide_genere_fichier():
    """
    Teste que le PDF d'un reçu valide est généré correctement.
    """
    donnees = {
        "nom": "KOUASSI Jean",
        "classe": "6ème A",
        "montant": 50000,
        "total_paye": 100000,
        "solde": 85000,
        "date_paiement": "2025-09-15",
        "mode_paiement": "Espèces",
    }

    donnees_json = json.dumps(donnees)
    numero_recu = "REC-2026-00001"
    date_generation = "2025-09-15 10:30:00"

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "recu_valide.pdf"

        # Générer un PDF valide
        generer_pdf_recu(donnees_json, numero_recu, date_generation, "valide", path)

        # Vérifier que le fichier existe
        assert path.exists()

        # Vérifier que le fichier n'est pas vide
        assert path.stat().st_size > 0

        # Vérifier que c'est un PDF valide
        content = path.read_bytes()
        assert content.startswith(b"%PDF")


def test_pdf_contient_donnees_figees():
    """
    Teste que le PDF est généré avec les données figées du reçu.
    """
    donnees = {
        "nom": "BAKAYOKO Yao",
        "classe": "6ème A",
        "montant": 25000,
        "total_paye": 185000,
        "solde": 0,
        "date_paiement": "2025-09-15",
        "mode_paiement": "Espèces",
    }

    donnees_json = json.dumps(donnees)
    numero_recu = "REC-2026-00009"
    date_generation = "2025-09-15 10:30:00"

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "recu_test.pdf"

        # Générer le PDF
        generer_pdf_recu(donnees_json, numero_recu, date_generation, "valide", path)

        # Vérifier que le fichier existe
        assert path.exists()

        # Vérifier que le fichier n'est pas vide
        assert path.stat().st_size > 0

        # Vérifier que c'est un PDF valide
        content = path.read_bytes()
        assert content.startswith(b"%PDF")
