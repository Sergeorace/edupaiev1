# Gestion Scolarité

Application desktop de gestion des élèves et des frais scolaires.

## Architecture

- **UI** : PySide6 (interface graphique)
- **Services** : Logique métier
- **Repositories** : Accès aux données
- **Database** : SQLite via sqlite3 (stdlib)

## Installation

```bash
pip install -r requirements.txt
```

## Initialisation de la base de données

```bash
python -m database.database
```

## Tests

```bash
pytest
```

## Hypothèses

- Année scolaire fixe : 2025-2026
- Devise : FCFA
- Montants entiers
- Un élève n'est jamais supprimé (archivage uniquement)
- Un paiement n'est jamais supprimé (annulation possible)
