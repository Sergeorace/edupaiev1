# Explications du projet

## ÉTAPE 1/4 : Couche données

### Ce qui a été réalisé

Cette étape a permis de mettre en place toute la couche données de l'application, qui constitue la fondation du système de gestion de scolarité.

#### 1. Structure du projet
- Initialisation du dépôt Git
- Création du fichier `.gitignore` pour exclure les fichiers de build, cache Python, et la base de données
- Création de l'arborescence complète : `database/`, `models/`, `repositories/`, `services/`, `ui/`, `utils/`, `reports/`, `resources/`, `tests/`
- Création de `requirements.txt` avec les versions figées de PySide6 et pytest

#### 2. Base de données SQLite
- **schema.sql** : Définition de 6 tables avec leurs relations :
  - `annees_scolaires` : Années scolaires avec dates de début/fin
  - `classes` : Classes avec niveau
  - `frais_classe` : Grille de frais par classe et année (Inscription, Scolarité, Autres)
  - `eleves` : Informations des élèves (matricule unique, nom, prénom, date de naissance, sexe, classe, tuteur, téléphone, statut actif/archivé)
  - `paiements` : Paiements avec statut (valide/annulé), motif d'annulation
  - `recus` : Reçus avec numéro unique séquentiel et données figées en JSON
- Contraintes d'intégrité : clés étrangères, CHECK (montant > 0), index pour optimiser les recherches
- **seed.sql** : Jeu de données de test réaliste avec 1 année, 4 classes, 20 élèves, 40 paiements (couvrant les 3 statuts : impayé, partiel, payé) et 2 paiements annulés

#### 3. Module database.py
- Fonction `create_connection()` : Crée une connexion SQLite avec activation des clés étrangères
- Context manager `get_transaction()` : Gère automatiquement commit/rollback des transactions
- Fonction `init_database()` : Génère la base de données depuis schema.sql et seed.sql
- Exécutable en ligne de commande : `python -m database.database`

#### 4. Modèles (dataclasses)
- **Eleve** : Représente un élève avec tous ses attributs, propriété `nom_complet`
- **Paiement** : Représente un paiement avec ses détails et statut
- **Recu** : Représente un reçu avec numéro unique et données JSON figées

#### 5. Repositories (accès aux données)
- **EleveRepository** :
  - CRUD complet (create, get_by_id, get_by_matricule, get_all, update)
  - Recherche avancée (par nom, prénom, matricule, classe)
  - Archivage (mise à actif = 0, sans suppression)
- **PaiementRepository** :
  - Création de paiements
  - Récupération par élève et/ou année
  - Calcul de la somme des paiements valides (exclut les annulés)
  - Annulation de paiement avec motif
- **RecuRepository** :
  - Création de reçus
  - Récupération par numéro, paiement, année
  - Obtention du dernier numéro de reçu pour une année (utile pour générer le numéro séquentiel suivant)

#### 6. Tests unitaires
- Tests complets pour les 3 repositories avec pytest
- Utilisation d'une base SQLite en mémoire pour isolation
- Couverture des cas : création, lecture, recherche, mise à jour, archivage, annulation
- Tests des règles métier : somme des paiements valides uniquement

### Points clés pour la défense orale

1. **Séparation des responsabilités** : L'architecture en couches (UI → Services → Repositories → Database) permet une maintenance facile et des tests isolés.

2. **Gestion des transactions** : Le context manager `get_transaction()` garantit l'intégrité des données : soit toutes les opérations réussissent (commit), soit aucune n'est appliquée (rollback).

3. **SQL paramétré** : Toutes les requêtes SQL utilisent des paramètres (`?`) pour éviter les injections SQL et permettre la réutilisation des plans d'exécution.

4. **Données figées dans les reçus** : Les reçus stockent les données en JSON au moment du paiement, ce qui permet de conserver l'historique même si l'élève change de classe ou si les frais sont modifiés ultérieurement.

5. **Archivage vs suppression** : Conformément aux règles métier, les élèves ne sont jamais supprimés mais archivés, ce qui permet de conserver l'historique complet des paiements.

6. **Tests en mémoire** : L'utilisation d'une base SQLite en mémoire (`:memory:`) rend les tests rapides et isolés, sans pollution de la base de développement.

### Hypothèses supplémentaires

- Les montants sont stockés en entiers (FCFA) dans la base de données
- Les dates sont stockées au format ISO (YYYY-MM-DD)
- Le numéro de reçu suit le format REC-AAAA-NNNNN où AAAA est l'année civile et NNNNN un numéro séquentiel
- Les modes de paiement possibles sont : Espèces, Chèque, Virement, Mobile
