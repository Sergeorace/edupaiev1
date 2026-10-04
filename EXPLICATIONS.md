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
- Version de PySide6 adaptée à Python 3.13 : 6.11.2 (au lieu de 6.6.3.1 initialement prévu)

---

## ÉTAPE 2/4 : Couche métier

### Ce qui a été réalisé

Cette étape a permis de mettre en place toute la logique métier de l'application, qui orchestre les opérations entre l'interface utilisateur et la couche données.

#### 1. Utils (utilitaires)

- **exceptions.py** : Exceptions personnalisées pour la couche métier
  - `ValidationError` : Erreur de validation des données
  - `RegleMetierError` : Violation d'une règle métier
  - `PaiementSuperieurAuSoldeError` : Paiement dépasse le solde restant
  - `EntiteIntrouvableError` : Entité non trouvée

- **validators.py** : Fonctions de validation des données
  - `validate_required()` : Vérifie qu'un champ n'est pas vide
  - `validate_montant()` : Vérifie qu'un montant est un entier positif
  - `validate_date()` : Vérifie qu'une date est valide (optionnellement pas dans le futur)
  - `validate_telephone()` : Vérifie le format d'un numéro de téléphone
  - `validate_matricule()` : Vérifie le format d'un matricule
  - `validate_sexe()` : Vérifie que le sexe est 'M' ou 'F'

- **formatters.py** : Fonctions de formatage pour l'affichage
  - `format_montant()` : Formate un montant avec séparateur de milliers (ex: "25 000 FCFA")
  - `format_date()` : Formate une date au format JJ/MM/AAAA
  - `format_statut()` : Formate un statut avec la première lettre en majuscule

- **date_utils.py** : Utilitaires pour la manipulation des dates
  - `parse_date()` : Parse une chaîne en date (JJ/MM/AAAA ou YYYY-MM-DD)
  - `get_annee_civile()` : Retourne l'année civile actuelle
  - `extract_annee_from_recu_numero()` : Extrait l'année d'un numéro de reçu

#### 2. Repositories supplémentaires

- **FraisClasseRepository** : Accès aux grilles de frais par classe et année
  - `get_by_classe_and_annee()` : Récupère la grille de frais
  - `get_total_by_classe_and_annee()` : Calcule le total des frais

- **DashboardRepository** : Requêtes d'agrégation pour le dashboard
  - `get_total_encaisse()` : Total des paiements valides
  - `get_total_restant_du()` : Total des soldes restants
  - `get_nombre_eleves_par_statut()` : Compte les élèves par statut (Impayé, Partiel, Payé)
  - `get_derniers_paiements()` : Récupère les derniers paiements

#### 3. Services (logique métier)

- **EleveService** : Gestion des élèves avec validation
  - `create_eleve()` : Création avec validation (matricule unique, champs obligatoires)
  - `update_eleve()` : Mise à jour avec validation et vérification d'unicité du matricule
  - `archive_eleve()` : Archivage (pas de suppression)
  - `get_eleve_by_id()`, `get_eleve_by_matricule()` : Récupération
  - `list_eleves()` : Liste des élèves (actifs ou tous)
  - `search_eleves()` : Recherche multi-critères

- **PaiementService** : Gestion des paiements avec règles métier
  - `calculer_frais_dus()` : Calcule les frais dus d'un élève (somme de la grille de sa classe)
  - `calculer_total_paye()` : Calcule le total des paiements valides
  - `calculer_solde()` : Calcule le solde restant (frais dus - total payé)
  - `calculer_statut()` : Détermine le statut (Impayé, Partiel, Payé)
  - `enregistrer_paiement()` : Enregistrement dans une transaction unique
    - Vérifie que le paiement ne dépasse pas le solde
    - Insère le paiement
    - Génère le numéro de reçu
    - Insère le reçu avec données figées (JSON)
    - Transaction atomique : tout ou rien
  - `annuler_paiement()` : Annulation avec motif obligatoire

- **RecuService** : Gestion des reçus
  - `get_recu_by_numero()` : Récupération par numéro
  - `get_recu_by_paiement()` : Récupération par paiement
  - `get_recus_by_annee()` : Liste des reçus d'une année
  - `generer_numero_recu()` : Génération du numéro séquentiel unique

- **DashboardService** : Statistiques pour le dashboard
  - `get_total_encaisse()` : Total encaissé
  - `get_total_restant_du()` : Total restant dû
  - `get_nombre_eleves_par_statut()` : Répartition par statut
  - `get_derniers_paiements()` : Derniers paiements enregistrés

#### 4. Tests unitaires

- Tests complets pour les validateurs (champs obligatoires, montants, dates, téléphones)
- Tests pour les formatters (montants, dates)
- Tests pour EleveService (création, mise à jour, archivage, validation, unicité du matricule)
- Tests pour PaiementService (calculs, enregistrement, contrôle du solde, annulation)
- Tests pour RecuService (récupération, génération de numéro)
- Tests pour DashboardService (statistiques, agrégations)
- Tests des cas limites : montant 0, négatif, date future, dépassement du solde, annulation sans motif
- ✅ Tous les tests passent (46/46)

### Points clés pour la défense orale

1. **Séparation des responsabilités** : Les services contiennent la logique métier et les validations, tandis que les repositories gèrent uniquement l'accès aux données. Aucun SQL dans les services.

2. **Validation des données** : Toutes les entrées sont validées avant d'être transmises aux repositories. Les erreurs de validation remontent sous forme d'exceptions avec des messages clairs pour l'utilisateur.

3. **Gestion des transactions** : L'enregistrement d'un paiement utilise une transaction atomique pour garantir la cohérence : paiement + reçu sont insérés ensemble ou pas du tout. En cas d'erreur, tout est annulé (rollback).

4. **Contrôle du solde** : Le service empêche tout paiement qui dépasserait le solde restant, avec une exception `PaiementSuperieurAuSoldeError` et un message explicite.

5. **Données figées dans les reçus** : Lors de l'enregistrement d'un paiement, le reçu stocke les données figées (nom, classe, montant, total payé, solde) en JSON. Cela permet de conserver l'historique même si l'élève change de classe ou si les frais sont modifiés ultérieurement.

6. **Numérotation séquentielle des reçus** : Le numéro de reçu est généré automatiquement avec le format REC-AAAA-NNNNN. La transaction garantit qu'il n'y a ni doublon ni trou en cas d'échec.

7. **Tests complets** : Les tests couvrent les cas nominaux et les cas limites (montants invalides, dates futures, dépassement de solde, annulation sans motif). L'utilisation d'une base en mémoire garantit l'isolation des tests.
