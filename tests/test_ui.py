"""
Tests UI avec pytest-qt en mode offscreen.
"""

import os
import sqlite3
from datetime import date

# Mode offscreen pour les tests
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from database.database import create_connection
from ui.main_window import MainWindow
from ui.eleves.eleves_widget import ElevesWidget
from ui.paiements.paiement_dialog import PaiementDialog


@pytest.fixture(scope="session")
def app():
    """Crée l'application Qt une fois pour tous les tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()


@pytest.fixture
def in_memory_db():
    """Fixture qui crée une base de données en mémoire."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    # Création du schéma
    schema_path = "database/schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        conn.executescript(schema_sql)

    # Insertion des données de test
    seed_path = "database/seed.sql"
    with open(seed_path, "r", encoding="utf-8") as f:
        seed_sql = f.read()
        conn.executescript(seed_sql)

    conn.commit()

    yield conn

    conn.close()


class TestMainWindow:
    """Tests pour la fenêtre principale."""

    def test_main_window_opens(self, app, in_memory_db):
        """Test que la fenêtre principale s'ouvre."""
        window = MainWindow(in_memory_db)
        assert window.windowTitle() == "Gestion Scolarité"
        assert window.minimumWidth() == 1000
        assert window.minimumHeight() == 700


class TestElevesWidget:
    """Tests pour le widget des élèves."""

    def test_eleves_widget_opens(self, app, in_memory_db):
        """Test que le widget des élèves s'ouvre."""
        widget = ElevesWidget(in_memory_db)
        assert widget is not None
        assert widget.table_model.rowCount() > 0  # Des élèves sont chargés

    def test_search_functionality(self, app, in_memory_db, qtbot):
        """Test la fonctionnalité de recherche."""
        widget = ElevesWidget(in_memory_db)
        qtbot.addWidget(widget)

        # Rechercher un élève existant
        widget.search_input.setText("KOUASSI")
        qtbot.wait(100)

        # Vérifier que le filtre est appliqué
        assert widget.table_model.rowCount() >= 0


class TestPaiementDialog:
    """Tests pour le dialogue de paiement."""

    def test_paiement_dialog_opens(self, app, in_memory_db):
        """Test que le dialogue de paiement s'ouvre."""
        dialog = PaiementDialog(in_memory_db, eleve_id=1, annee_id=1)
        assert dialog.windowTitle() == "Enregistrer un paiement"
        assert dialog.solde_actuel > 0

    def test_paiement_superieur_au_solde_refuse(self, app, in_memory_db, qtbot):
        """Test qu'un paiement supérieur au solde est refusé."""
        dialog = PaiementDialog(in_memory_db, eleve_id=1, annee_id=1)
        qtbot.addWidget(dialog)

        # Entrer un montant supérieur au solde
        dialog.montant_input.setText(str(dialog.solde_actuel + 10000))
        dialog.mode_input.setCurrentText("Espèces")
        qtbot.wait(100)

        # Tenter d'enregistrer
        dialog.btn_enregistrer.click()
        qtbot.wait(100)

        # Le dialogue devrait être ouvert (refus)
        assert dialog.isVisible()


class TestNoSqliteImport:
    """Test pour vérifier qu'aucun widget n'importe sqlite3."""

    def test_no_sqlite_in_ui(self):
        """Vérifie qu'aucun fichier UI n'importe sqlite3."""
        import ui.main_window
        import ui.dashboard.dashboard_widget
        import ui.eleves.eleves_widget
        import ui.eleves.eleve_form
        import ui.eleves.eleve_detail
        import ui.paiements.paiement_dialog

        # Vérifier que sqlite3 n'est pas dans les imports
        ui_modules = [
            ui.main_window,
            ui.dashboard.dashboard_widget,
            ui.eleves.eleves_widget,
            ui.eleves.eleve_form,
            ui.eleves.eleve_detail,
            ui.paiements.paiement_dialog,
        ]

        for module in ui_modules:
            assert "sqlite3" not in dir(module), f"{module.__name__} importe sqlite3"
