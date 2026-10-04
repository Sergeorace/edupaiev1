"""Tests PySide6 exécutés sans serveur graphique."""

import os
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from database.database import create_connection
from services.eleve_service import EleveService
from services.paiement_service import PaiementService
from ui.eleves.eleve_form import EleveFormDialog
from ui.eleves.eleves_widget import ElevesWidget
from ui.main_window import MainWindow
from ui.paiements.paiement_dialog import PaiementDialog


@pytest.fixture(scope="session")
def app():
    """Crée une seule application Qt pour toute la session de tests."""
    application = QApplication.instance() or QApplication([])
    yield application
    application.quit()


@pytest.fixture
def in_memory_db():
    """Prépare une base mémoire avec le schéma et les données d'exemple."""
    conn = create_connection(":memory:")
    database_dir = Path(__file__).resolve().parents[1] / "database"
    conn.executescript(
        (database_dir / "schema.sql").read_text(encoding="utf-8")
    )
    conn.executescript(
        (database_dir / "seed.sql").read_text(encoding="utf-8")
    )
    conn.commit()
    yield conn
    conn.close()


class TestMainWindow:
    """Vérifie l'assemblage des écrans principaux."""

    def test_main_window_opens(self, app, in_memory_db, qtbot):
        """La fenêtre s'ouvre et contient les trois pages attendues."""
        window = MainWindow(in_memory_db)
        qtbot.addWidget(window)
        window.show()

        assert window.windowTitle() == "Gestion Scolarité"
        assert window.minimumWidth() == 1000
        assert window.minimumHeight() == 700
        assert window.stacked_widget.count() == 3


class TestElevesWidget:
    """Vérifie les interactions de la liste des élèves."""

    def test_search_matches_name_first_name_or_matricule(
        self, app, in_memory_db, qtbot
    ):
        """La recherche retrouve une correspondance dans chacun des champs."""
        widget = ElevesWidget(in_memory_db)
        qtbot.addWidget(widget)

        widget.search_input.setText("KOUASSI")
        assert widget.table_model.rowCount() == 1

        widget.search_input.setText("Jean")
        assert widget.table_model.rowCount() == 1

        widget.search_input.setText("MAT001")
        assert widget.table_model.rowCount() == 1
        assert widget.table_model.get_eleve_at(0).matricule == "MAT001"

    def test_filter_by_class_and_status(self, app, in_memory_db, qtbot):
        """Le filtre classe/statut agit sur les élèves chargés."""
        widget = ElevesWidget(in_memory_db)
        qtbot.addWidget(widget)

        class_index = widget.classe_filter.findData(1)
        widget.classe_filter.setCurrentIndex(class_index)
        assert widget.table_model.rowCount() == 5

        widget.statut_filter.setCurrentText("Impayé")
        assert widget.table_model.rowCount() == 0


class TestEleveForm:
    """Teste la création d'un élève depuis le formulaire UI."""

    def test_add_student_through_form(
        self, app, in_memory_db, qtbot, monkeypatch
    ):
        """Les données du formulaire sont envoyées au service et persistées."""
        monkeypatch.setattr(QMessageBox, "information", lambda *args: None)
        dialog = EleveFormDialog(in_memory_db)
        qtbot.addWidget(dialog)
        dialog.matricule_input.setText("MAT900")
        dialog.nom_input.setText("TRAORE")
        dialog.prenom_input.setText("Awa")
        dialog.sexe_input.setCurrentText("F")
        dialog.classe_input.setCurrentIndex(0)
        dialog.tuteur_input.setText("TRAORE Adama")
        dialog.telephone_input.setText("0700000090")

        dialog._on_enregistrer()

        assert dialog.result() == dialog.DialogCode.Accepted
        assert EleveService(in_memory_db).get_eleve_by_matricule("MAT900") is not None


class TestPaiementDialog:
    """Vérifie le refus des paiements dépassant le solde."""

    def test_amount_over_balance_is_disabled_and_shown(
        self, app, in_memory_db, qtbot, monkeypatch
    ):
        """Un montant excessif affiche un message et n'est pas persisté."""
        messages = []
        monkeypatch.setattr(
            QMessageBox, "warning", lambda *args: messages.append(args[2])
        )
        service = PaiementService(in_memory_db)
        initial_total = service.calculer_total_paye(1, 1)
        initial_count = len(service.get_paiements_eleve(1, 1))
        dialog = PaiementDialog(in_memory_db, eleve_id=1, annee_id=1)
        qtbot.addWidget(dialog)

        dialog.montant_input.setText(str(dialog.solde_actuel + 10000))
        assert not dialog.btn_enregistrer.isEnabled()
        assert "dépasse le solde" in dialog.validation_label.text()

        dialog._on_enregistrer()

        assert messages
        assert service.calculer_total_paye(1, 1) == initial_total
        assert len(service.get_paiements_eleve(1, 1)) == initial_count


class TestNoSqliteImport:
    """Vérifie que l'interface ne dépend pas directement de sqlite3."""

    def test_no_sqlite_in_ui(self):
        """Aucun module UI ne lie le module sqlite3."""
        import ui.dashboard.dashboard_widget
        import ui.eleves.eleve_detail
        import ui.eleves.eleve_form
        import ui.eleves.eleves_widget
        import ui.main_window
        import ui.paiements.paiement_dialog
        import ui.recus.recu_viewer

        ui_modules = (
            ui.dashboard.dashboard_widget,
            ui.eleves.eleve_detail,
            ui.eleves.eleve_form,
            ui.eleves.eleves_widget,
            ui.main_window,
            ui.paiements.paiement_dialog,
            ui.recus.recu_viewer,
        )
        for module in ui_modules:
            assert "sqlite3" not in vars(module)
