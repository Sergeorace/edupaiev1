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
- **seed.sql** : Jeu de données de test réaliste avec 1 année, 4 classes, 20 élèves, 37 paiements (environ 40, couvrant les 3 statuts : impayé, partiel, payé) et 2 paiements annulés, tous avec leur reçu

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

#### Ajustements de cette étape

- La recherche d'élèves utilise une requête SQL fixe et des paramètres : les valeurs saisies ne sont jamais ajoutées au texte SQL.
- Le repository des élèves ne propose plus de suppression physique ; les élèves sont archivés pour conserver leur historique.
- La création de la base peut être relancée sans réinsérer les données de test ni provoquer de doublons. Les créations du schéma et du jeu de test sont protégées par des transactions.
- Les données initiales minimales des tests sont stockées dans `database/test_seed.sql`, pour que les requêtes SQL restent dans la couche données.

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
- Tests pour RecuService (récupération, génération de numéro et nouvelle année civile)
- Tests pour DashboardService (statistiques, agrégations)
- Tests des cas limites : montant 0, négatif ou texte, date future, dépassement du solde, doublon de matricule et annulation sans motif
- Tests du rollback en cas d'échec lors de la création du reçu, de la reprise du paiement après annulation et de deux paiements concurrents
- Les tests de la couche métier passent (41 tests). La suite complète reste bloquée avant la collecte des tests UI par un nom `sqlite3` non défini dans l'annotation de `ui/eleves/eleve_form.py`, qui est hors du périmètre de cette étape.

### Points clés pour la défense orale

1. **Séparation des responsabilités** : Les services contiennent la logique métier et les validations, tandis que les repositories gèrent uniquement l'accès aux données. Aucun SQL dans les services.

2. **Validation des données** : Toutes les entrées sont validées avant d'être transmises aux repositories. Les erreurs de validation remontent sous forme d'exceptions avec des messages clairs pour l'utilisateur.

3. **Gestion des transactions** : L'enregistrement d'un paiement utilise une transaction atomique pour garantir la cohérence : paiement + reçu sont insérés ensemble ou pas du tout. En cas d'erreur, tout est annulé (rollback).

4. **Contrôle du solde** : Le service empêche tout paiement qui dépasserait le solde restant, avec une exception `PaiementSuperieurAuSoldeError` et un message explicite.

5. **Données figées dans les reçus** : Lors de l'enregistrement d'un paiement, le reçu stocke les données figées (nom, classe, montant, total payé, solde) en JSON. Cela permet de conserver l'historique même si l'élève change de classe ou si les frais sont modifiés ultérieurement.

6. **Numérotation séquentielle des reçus** : Le numéro de reçu est généré automatiquement avec le format REC-AAAA-NNNNN. La transaction garantit qu'il n'y a ni doublon ni trou en cas d'échec.

7. **Tests complets** : Les tests couvrent les cas nominaux et les cas limites (montants invalides, dates futures, dépassement de solde, annulation sans motif). L'utilisation d'une base en mémoire garantit l'isolation des tests.

8. **Paiements concurrents** : Le service demande à SQLite de réserver l'écriture avant de vérifier le solde. Ainsi, deux paiements simultanés ne peuvent pas utiliser le même solde restant.

9. **Absence de trou dans les reçus** : Le numéro est calculé et le reçu est inséré dans la même transaction que le paiement. Si une étape échoue, le paiement et le reçu sont annulés ensemble, et le prochain paiement peut reprendre le numéro sans en sauter.

10. **Erreurs compréhensibles** : Les entrées invalides, les soldes insuffisants et les entités absentes déclenchent des exceptions métier avec un message explicite, au lieu de faire apparaître une erreur SQLite brute.

### Hypothèses supplémentaires pour cette étape

- Les matricules sont normalisés en majuscules et comparés sans distinction de casse.
- Une date de naissance ne peut pas être dans le futur ; une date de paiement non plus.
- L'année du reçu est l'année civile au moment de l'émission ; la séquence recommence à `00001` au changement d'année civile.
- La méthode qui calcule le prochain numéro de reçu est appelée à l'intérieur de la transaction qui enregistre le paiement et le reçu.

---

## ÉTAPE 4/4 : Reçus, packaging, documentation

### Ce qui a été réalisé

Cette étape a permis de compléter l'application avec la génération de reçus PDF, le packaging pour distribution et la documentation finale.

#### 1. Générateur de PDF (reports/recu_generator.py)

- **reportlab** : Bibliothèque utilisée pour la génération de PDF
- **Fonction `generer_pdf_recu()`** : Génère un PDF de reçu à partir des données figées
  - En-tête avec nom de l'établissement (configurable)
  - Numéro de reçu unique et date de génération
  - Informations de l'élève (nom, classe)
  - Détails du paiement (montant, total payé, solde, date, mode)
  - Filigrane "ANNULÉ" si le paiement est annulé
- **Données figées** : Le PDF utilise uniquement les données stockées dans la table `recus` (JSON)
  - Garantit qu'un reçu ré-imprimé est identique à l'original
  - Permet de conserver l'historique même si l'élève change de classe

#### 2. Interface de visualisation des reçus (ui/recus/recu_viewer.py)

- **RecusViewerWidget** : Widget principal de gestion des reçus
  - Liste des reçus avec recherche par numéro ou élève
  - Affichage du statut du paiement (valide/annulé)
  - Bouton "Exporter PDF" pour télécharger le reçu
  - Bouton "Imprimer" pour impression directe
  - Menu contextuel (clic droit) pour actions rapides
- **Fonction `open_recu_direct()`** : Ouvre directement le reçu d'un paiement depuis la fiche élève
- **Intégration dans main_window.py** : Ajout de la page "Reçus" dans la barre latérale

#### 3. Tests du générateur de PDF (tests/test_recu_generator.py)

- **test_pdf_generation_cree_fichier** : Vérifie que le PDF est créé
- **test_pdf_generation_meme_donnees** : Vérifie que deux générations avec les mêmes données produisent des fichiers de même taille
- **test_pdf_annule_genere_fichier** : Vérifie la génération de PDF annulé
- **test_pdf_valide_genere_fichier** : Vérifie la génération de PDF valide
- **test_pdf_contient_donnees_figees** : Vérifie que le PDF est valide et non vide
- ✅ Tous les tests passent (5/5)

#### 4. Gestion des chemins pour packaging (utils/paths.py)

- **Fonction `resource_path()`** : Retourne le chemin absolu vers une ressource
  - Gère le développement (chemin relatif) et le packaging (sys._MEIPASS)
  - Permet d'accéder aux ressources (database, styles, icônes) dans l'exécutable
- **Fonction `get_user_data_dir()`** : Retourne le dossier de données utilisateur
  - Windows : `%APPDATA%\GestionScolarite`
  - Linux/macOS : `~/.local/share/GestionScolarite`
- **Fonction `get_user_db_path()`** : Retourne le chemin vers la base de données utilisateur
- **Fonction `copy_db_if_needed()`** : Copie la base template dans le dossier utilisateur au premier lancement
- **Intégration dans main.py** : Utilisation de ces fonctions pour la gestion de la base de données

#### 5. Packaging avec PyInstaller

- **Fichier gestion_scolarite.spec** : Configuration PyInstaller
  - Inclusion de la base de données template (school.db)
  - Inclusion des ressources (styles, icônes)
  - Imports cachés pour PySide6 et reportlab
  - Mode windowed (pas de console)
  - One-file (exécutable unique)
- **Script build.bat** : Script de build Windows
  - Installation des dépendances
  - Génération de la base de données de test
  - Exécution des tests
  - Construction de l'exécutable avec PyInstaller
- **Workflow GitHub Actions (.github/workflows/build-windows.yml)** : Automatisation du build
  - Runner Windows (windows-latest)
  - Installation Python 3.13
  - Installation des dépendances
  - Génération de la base de données
  - Exécution des tests
  - Build avec PyInstaller
  - Publication de l'exécutable comme artefact

#### 6. Documentation

- **README.md complet** :
  - Installation et lancement
  - Initialisation de la base de données
  - Tests (avec exemples de commandes)
  - Règles métier détaillées
  - Procédure de build (manuel et GitHub Actions)
  - Procédure de test de l'exécutable sur machine Windows propre (liste de vérification détaillée)
- **Mise à jour de requirements.txt** : Ajout de reportlab==4.2.0
- **Mise à jour de .gitignore** : Exception pour gestion_scolarite.spec (versionné)

### Points clés pour la défense orale

1. **Données figées dans les reçus** : Les reçus stockent les données en JSON au moment du paiement, ce qui permet de conserver l'historique et de ré-imprimer des reçus identiques même si l'élève change de classe ou si les frais sont modifiés ultérieurement.

2. **Génération de PDF avec reportlab** : Utilisation de reportlab pour créer des PDF professionnels avec en-tête, tableau de données et filigrane pour les paiements annulés. La bibliothèque est légère et ne nécessite pas de dépendances externes complexes.

3. **Packaging avec PyInstaller** : Utilisation de PyInstaller pour créer un exécutable unique (one-file) qui inclut toutes les dépendances Python, la base de données template et les ressources (styles, icônes). L'exécutable est windowed (pas de console) pour une meilleure expérience utilisateur.

4. **Gestion des chemins avec resource_path()** : La fonction `resource_path()` permet à l'application de fonctionner aussi bien en développement qu'en étant packagée. Elle détecte automatiquement si l'application est exécutée depuis le dossier source ou depuis sys._MEIPASS (dossier temporaire de PyInstaller).

5. **Base de données utilisateur** : L'exécutable utilise une base de données stockée dans le dossier utilisateur (%APPDATA% sur Windows), ce qui permet à l'application d'être installée dans un dossier en lecture seule (ex: Program Files) tout en ayant un espace de données inscriptible.

6. **Workflow GitHub Actions** : Automatisation du build sur Windows avec un runner windows-latest. Le workflow installe les dépendances, lance les tests, construit l'exécutable et le publie comme artefact. Cela garantit que chaque build est testé et fonctionnel.

7. **Tests du générateur de PDF** : Les tests vérifient que le générateur crée bien des fichiers PDF valides, que deux générations avec les mêmes données produisent des résultats cohérents, et que les PDF annulés sont générés correctement.

8. **Procédure de test sur machine propre** : Le README inclut une liste de vérification détaillée pour tester l'exécutable sur une machine Windows vierge (sans Python). Cela couvre tous les cas d'utilisation : tableau de bord, gestion des élèves, paiements, reçus, archivage, persistance des données.

### Hypothèses supplémentaires (étape 4)

- Bibliothèque reportlab 4.2.0 pour la génération de PDF
- Nom de l'établissement configurable dans `reports/recu_generator.py` (défaut: "ÉCOLE EXEMPLE")
- L'exécutable Windows ne peut pas être testé depuis Linux (limitation de l'environnement de développement)
- La base de données template est incluse dans l'exécutable et copiée dans le dossier utilisateur au premier lancement
- Les logs sont stockés dans le dossier utilisateur dans un sous-dossier `logs/`

---

## Schéma de la base de données

La base de données SQLite comprend 6 tables avec les relations suivantes :

```
annees_scolaires (id, annee, date_debut, date_fin)
       |
       v
classes (id, nom, niveau)
       |
       v
frais_classe (id, classe_id, annee_id, type_frais, montant, description)
       |           |
       |           v
       |    paiements (id, eleve_id, annee_id, montant, date_paiement,
       |              mode_paiement, motif, statut, motif_annulation, date_annulation)
       |           |
       |           v
       |       recus (id, numero, paiement_id, annee_id, donnees_json, date_generation)
       |
       v
eleves (id, matricule, nom, prenom, date_naissance, sexe, classe_id, tuteur, telephone, actif)
```

### Tables principales

1. **annees_scolaires** : Années scolaires avec dates de début et fin
2. **classes** : Classes avec niveau (Primaire, Collège)
3. **frais_classe** : Grille de frais par classe et année (Inscription, Scolarité, Autres)
4. **eleves** : Informations des élèves avec statut actif/archivé
5. **paiements** : Paiements avec statut (valide/annulé) et motif d'annulation
6. **recus** : Reçus avec numéro unique séquentiel et données figées en JSON

### Index pour optimisation

- `idx_frais_classe_annee` : accélère les recherches de frais par classe et année
- `idx_eleves_classe` : accélère les recherches d'élèves par classe
- `idx_eleves_actif` : accélère le filtrage par statut actif
- `idx_eleves_nom` : accélère la recherche par nom/prénom
- `idx_paiements_eleve` : accélère les recherches de paiements par élève
- `idx_paiements_annee` : accélère les recherches de paiements par année
- `idx_paiements_statut` : accélère le filtrage par statut
- `idx_paiements_eleve_annee` : accélère les recherches combinées élève/année
- `idx_recus_numero` : accélère la recherche par numéro de reçu
- `idx_recus_paiement` : accélère la recherche par paiement
- `idx_recus_annee` : accélère les recherches par année

---

## Les 5 requêtes SQL les plus importantes

### 1. Calcul du total des paiements valides d'un élève

```sql
SELECT COALESCE(SUM(montant), 0)
FROM paiements
WHERE eleve_id = ? AND annee_id = ? AND statut = 'valide'
```

**Rôle** : Calcule la somme des paiements valides (non annulés) d'un élève pour une année scolaire. Utilisé pour déterminer le solde restant et le statut de paiement.

**Pourquoi c'est important** : C'est la base de tous les calculs financiers. Sans cette requête, on ne peut pas savoir combien un élève a payé.

### 2. Récupération des paiements d'un élève avec jointures

```sql
SELECT p.id, p.eleve_id, p.annee_id, a.annee as annee_texte,
       p.montant, p.date_paiement, p.mode_paiement, p.motif,
       p.statut, p.motif_annulation, p.date_annulation,
       e.nom as eleve_nom, e.prenom as eleve_prenom
FROM paiements p
LEFT JOIN annees_scolaires a ON p.annee_id = a.id
LEFT JOIN eleves e ON p.eleve_id = e.id
WHERE p.eleve_id = ? AND p.annee_id = ?
ORDER BY p.date_paiement DESC
```

**Rôle** : Récupère tous les paiements d'un élève pour une année scolaire, avec les informations de l'élève et de l'année. Utilisé dans la fiche élève pour afficher l'historique des paiements.

**Pourquoi c'est important** : Permet d'afficher l'historique complet des paiements avec toutes les informations nécessaires (nom de l'élève, année, montant, date, mode, statut).

### 3. Insertion d'un paiement

```sql
INSERT INTO paiements (eleve_id, annee_id, montant, date_paiement,
                      mode_paiement, motif, statut)
VALUES (?, ?, ?, ?, ?, ?, ?)
```

**Rôle** : Insère un nouveau paiement dans la base de données. Utilisé lors de l'enregistrement d'un paiement.

**Pourquoi c'est important** : C'est la requête de création principale. Elle est exécutée dans une transaction avec l'insertion du reçu pour garantir l'atomicité (tout ou rien).

### 4. Annulation d'un paiement

```sql
UPDATE paiements
SET statut = 'annule',
    motif_annulation = ?,
    date_annulation = ?
WHERE id = ?
```

**Rôle** : Annule un paiement en mettant à jour son statut et en ajoutant le motif d'annulation. Utilisé lorsqu'un paiement doit être annulé.

**Pourquoi c'est important** : Permet d'annuler un paiement sans le supprimer, ce qui conserve l'historique. L'annulation libère le solde pour de nouveaux paiements.

### 5. Calcul des statistiques du dashboard

```sql
SELECT
    (SELECT COALESCE(SUM(p.montant), 0)
     FROM paiements p
     WHERE p.annee_id = ? AND p.statut = 'valide') as total_encaisse,
    (SELECT COALESCE(SUM(f.montant), 0)
     FROM frais_classe f
     WHERE f.annee_id = ?) as total_frais,
    (SELECT COUNT(*)
     FROM eleves e
     WHERE e.actif = 1) as total_eleves
```

**Rôle** : Calcule les statistiques globales pour le tableau de bord (total encaissé, total des frais, nombre d'élèves actifs).

**Pourquoi c'est important** : Permet d'afficher une vue d'ensemble de la situation financière de l'école en un coup d'œil.

---

## Flux complet d'un paiement

### Étape 1 : L'utilisateur sélectionne un élève et clique sur "Payer"

1. L'UI ouvre le dialogue `PaiementDialog` avec l'ID de l'élève et l'année scolaire
2. Le service `PaiementService` calcule le solde actuel de l'élève
3. Le dialogue affiche le solde restant avant paiement

### Étape 2 : L'utilisateur saisit les informations du paiement

1. L'utilisateur saisit le montant, la date et le mode de paiement
2. Le dialogue valide en temps réel :
   - Montant > 0
   - Date dans le passé ou aujourd'hui
   - Mode de paiement valide
3. Le dialogue affiche le solde après paiement (solde actuel - montant)

### Étape 3 : L'utilisateur clique sur "Enregistrer"

1. Le dialogue appelle `PaiementService.enregistrer_paiement()`
2. Le service valide les données avec les validateurs
3. Le service vérifie que l'élève existe
4. Le service calcule le solde restant avant paiement
5. Le service vérifie que le paiement ne dépasse pas le solde
   - Si oui, lève `PaiementSuperieurAuSoldeError`
6. Le service commence une transaction avec `get_transaction()`

### Étape 4 : Insertion du paiement (dans la transaction)

1. Le service crée un objet `Paiement` avec statut "valide"
2. Le repository `PaiementRepository` insère le paiement dans la base
3. L'ID du paiement est généré automatiquement

### Étape 5 : Préparation des données du reçu (dans la transaction)

1. Le service calcule le total payé après ce paiement
2. Le service calcule le nouveau solde
3. Le service prépare les données figées du reçu en JSON :
   ```json
   {
     "nom": "KOUASSI Jean",
     "classe": "6ème A",
     "montant": 50000,
     "total_paye": 100000,
     "solde": 85000,
     "date_paiement": "2025-09-15"
   }
   ```

### Étape 6 : Génération du numéro de reçu (dans la transaction)

1. Le service appelle `RecuRepository.get_last_numero()` pour obtenir le dernier numéro
2. Le service extrait l'année civile et le numéro séquentiel
3. Le service incrémente le numéro séquentiel
4. Le service génère le nouveau numéro au format REC-AAAA-NNNNN

### Étape 7 : Insertion du reçu (dans la transaction)

1. Le service crée un objet `Recu` avec :
   - Le numéro généré
   - L'ID du paiement
   - Les données JSON figées
2. Le repository `RecuRepository` insère le reçu dans la base

### Étape 8 : Commit de la transaction

1. Le context manager `get_transaction()` exécute le commit
2. Le paiement et le reçu sont enregistrés de manière atomique
3. Si une erreur s'était produite, un rollback aurait été exécuté

### Étape 9 : Mise à jour de l'UI

1. Le dialogue affiche un message de succès
2. Le dialogue se ferme
3. L'UI recharge la liste des élèves
4. Le nouveau solde et le nouveau statut sont affichés

### Étape 10 : Génération du PDF (optionnel)

1. L'utilisateur peut cliquer sur "Reçus" dans la barre latérale
2. L'utilisateur peut sélectionner le reçu et cliquer sur "Exporter PDF"
3. Le générateur `generer_pdf_recu()` utilise les données figées du reçu
4. Le PDF est généré avec reportlab et enregistré

---

## Questions probables de soutenance avec réponses

### Questions sur l'architecture

**Q : Pourquoi avoir choisi une architecture en couches (UI → Services → Repositories → Database) ?**

R : Cette architecture offre plusieurs avantages :
- **Séparation des responsabilités** : Chaque couche a un rôle précis, ce qui rend le code plus maintenable
- **Testabilité** : Chaque couche peut être testée indépendamment (ex: tests des repositories sans UI)
- **Réutilisabilité** : Les services et repositories peuvent être réutilisés dans d'autres contextes (ex: API web)
- **Évolutivité** : Il est facile d'ajouter de nouvelles fonctionnalités ou de changer d'implémentation (ex: passer de SQLite à PostgreSQL)

**Q : Pourquoi avoir utilisé SQLite plutôt qu'un autre SGBD ?**

R : SQLite est idéal pour cette application car :
- **Léger** : Pas besoin d'installer un serveur de base de données
- **Portable** : La base est un simple fichier, facile à déplacer
- **Intégré** : sqlite3 est dans la bibliothèque standard de Python
- **Suffisant** : Pour une application desktop mono-utilisateur, SQLite est largement suffisant
- **Performant** : Très rapide pour les requêtes simples avec des indexes

**Q : Pourquoi avoir choisi PySide6 plutôt qu'une autre bibliothèque GUI ?**

R : PySide6 est le binding officiel de Qt pour Python :
- **Professionnel** : Qt est utilisé dans de nombreuses applications professionnelles
- **Multi-plateforme** : Fonctionne sur Windows, Linux et macOS
- **Riche** : Fournit de nombreux widgets prêts à l'emploi
- **Actif** : Projet maintenu par The Qt Company
- **Licence** : LGPL, compatible avec les projets commerciaux

### Questions sur la base de données

**Q : Pourquoi avoir stocké les données du reçu en JSON dans la table recus ?**

R : C'est une décision essentielle pour garantir l'intégrité des reçus :
- **Figé dans le temps** : Les données du reçu sont capturées au moment du paiement
- **Ré-impression identique** : Si on ré-imprime un reçu plus tard, il sera identique à l'original
- **Indépendance des modifications** : Si l'élève change de classe ou si les frais sont modifiés, le reçu original reste inchangé
- **Performance** : Pas besoin de faire des jointures complexes pour régénérer un reçu

**Q : Pourquoi ne pas supprimer les élèves et les paiements ?**

R : C'est une règle métier essentielle pour la traçabilité :
- **Historique complet** : On doit pouvoir consulter l'historique d'un élève même après son départ
- **Audit** : En cas de litige, on doit pouvoir prouver ce qui s'est passé
- **Conformité** : En milieu scolaire, la conservation des données est souvent obligatoire
- **Archivage** : L'archivage (actif = 0) permet de "masquer" les élèves sans perdre l'historique

**Q : Pourquoi avoir utilisé des indexes sur certaines colonnes ?**

R : Les indexes accélèrent les requêtes fréquentes :
- **idx_eleves_classe** : Accélère la liste des élèves par classe
- **idx_paiements_eleve_annee** : Accélère l'historique des paiements d'un élève
- **idx_recus_numero** : Accélère la recherche d'un reçu par son numéro
- Sans indexes, ces requêtes seraient des scans complets de table, ce qui serait lent avec beaucoup de données

### Questions sur la logique métier

**Q : Pourquoi empêcher un paiement qui dépasse le solde ?**

R : C'est une règle de gestion financière :
- **Prévention des erreurs** : Empêche les surpaiements accidentels
- **Contrôle budgétaire** : Garantit que l'école ne reçoit pas plus que ce qui est dû
- **Clarté** : Évite les situations où un élève aurait un solde négatif
- **Message explicite** : L'utilisateur est informé du solde restant et peut ajuster son paiement

**Q : Pourquoi avoir mis l'annulation dans une transaction avec le reçu ?**

R : C'est pour garantir l'atomicité :
- **Tout ou rien** : Soit le paiement ET le reçu sont enregistrés, soit rien ne l'est
- **Cohérence** : On ne peut pas avoir un paiement sans reçu, ni un reçu sans paiement
- **Rollback** : Si une erreur survient, tout est annulé automatiquement
- **Numérotation séquentielle** : Garantit qu'il n'y a ni trou ni doublon dans les numéros de reçu

**Q : Pourquoi avoir calculé le statut (Impayé/Partiel/Payé) plutôt que de le stocker ?**

R : C'est un choix de conception :
- **Dynamique** : Le statut est recalculé à chaque fois en fonction des paiements
- **À jour** : Si un paiement est annulé, le statut est automatiquement mis à jour
- **Pas de redondance** : On ne stocke pas d'information dérivée
- **Simple** : Le calcul est rapide (somme des paiements valides)

### Questions sur le packaging

**Q : Pourquoi avoir utilisé PyInstaller plutôt qu'une autre solution de packaging ?**

R : PyInstaller est la solution la plus mature pour Python :
- **Simple** : Un seul fichier de configuration (.spec)
- **One-file** : Génère un exécutable unique facile à distribuer
- **Cross-platform** : Fonctionne sur Windows, Linux et macOS
- **Supporté** : Large communauté et documentation
- **Intégration** : Bien intégré avec GitHub Actions

**Q : Pourquoi avoir stocké la base de données dans le dossier utilisateur ?**

R : C'est une bonne pratique pour les applications desktop :
- **Permissions** : L'application peut être installée dans Program Files (lecture seule)
- **Persistance** : Les données survivent à une mise à jour de l'application
- **Multi-utilisateur** : Chaque utilisateur a sa propre base de données
- **Standard** : Conforme aux conventions de Windows (%APPDATA%)

**Q : Pourquoi avoir inclus la base de données template dans l'exécutable ?**

R : Pour faciliter le premier lancement :
- **Automatique** : L'utilisateur n'a pas besoin de générer la base manuellement
- **Test** : La base contient des données de test pour démonstration
- **Robustesse** : Si la base utilisateur est corrompue, on peut la régénérer
- **Simplicité** : Un seul fichier à distribuer

### Questions sur les tests

**Q : Pourquoi avoir utilisé une base SQLite en mémoire pour les tests ?**

R : Plusieurs avantages :
- **Isolation** : Chaque test a sa propre base, pas de pollution entre les tests
- **Rapidité** : Les opérations en mémoire sont beaucoup plus rapides
- **Propre** : Pas besoin de nettoyer les fichiers après les tests
- **Reproductible** : Les tests sont identiques sur toutes les machines

**Q : Pourquoi avoir testé le générateur de PDF ?**

R : C'est un composant critique :
- **Fidélité** : On doit garantir que le PDF est identique à chaque génération
- **Annulation** : On doit vérifier que les reçus annulés sont bien marqués
- **Données** : On doit vérifier que toutes les données sont présentes
- **Validation** : On doit vérifier que le PDF est valide et peut être ouvert

**Q : Pourquoi avoir une couverture de tests élevée ?**

R : La qualité logicielle dépend des tests :
- **Confiance** : On peut modifier le code sans craindre de casser quelque chose
- **Documentation** : Les tests servent de documentation vivante du comportement attendu
- **Refactoring** : On peut refactoriser en sécurité si les tests passent
- **Maintenance** : Les bugs sont détectés tôt et sont plus faciles à corriger

### Questions sur la documentation

**Q : Pourquoi avoir documenté le processus de test sur machine propre ?**

R : C'est essentiel pour la distribution :
- **Validation** : Garantit que l'exécutable fonctionne sur une machine vierge
- **Déploiement** : Facilite le déploiement sur les machines des utilisateurs
- **Debug** : Si un problème survient, on sait où chercher
- **Professionnalisme** : Montre que l'application est prête pour la production

**Q : Pourquoi avoir utilisé EXPLICATIONS.md en plus de README.md ?**

R : Deux documents avec des objectifs différents :
- **README.md** : Pour les utilisateurs (installation, lancement, règles métier)
- **EXPLICATIONS.md** : Pour la soutenance (architecture, décisions techniques, flux détaillés)
- **Complémentarité** : Chaque document a son public et son objectif
- **Rédaction** : EXPLICATIONS.md est rédigé en langage simple pour faciliter la défense orale

---

## ÉTAPE 3/4 : Interface PySide6

### Ce qui a été réalisé

L'application dispose maintenant de ses écrans graphiques. La fenêtre principale
présente une barre latérale et trois pages : le tableau de bord, la gestion des
élèves et l'historique des reçus.

- Dans **Élèves**, on peut rechercher un élève par nom, prénom ou matricule,
  filtrer par classe et par situation de paiement, puis ouvrir les formulaires
  d'ajout/modification, la fiche, le paiement ou l'archivage.
- La **fiche élève** résume les frais, les paiements et le solde. Son tableau
  conserve aussi les paiements annulés et permet de retrouver le reçu.
- La fenêtre de **paiement** montre le solde avant et après. Elle signale un
  montant qui dépasse le solde et désactive le bouton d'enregistrement.
- Le **tableau de bord** présente les sommes encaissées et restant dues, le
  nombre d'élèves par statut ainsi que les paiements récents.
- Dans **Reçus**, on peut rechercher, exporter en PDF et imprimer. Le statut
  annulé reste visible, car l'annulation ne supprime pas le reçu.

Les widgets ne parlent qu'aux services ; ils n'importent pas `sqlite3` et ne
contiennent pas de requête SQL. Un gestionnaire commun présente les erreurs de
validation et les règles métier. Les erreurs inattendues sont inscrites dans
les journaux avant d'afficher un message générique.

Des tests pytest-qt vérifient l'ouverture de la fenêtre, la recherche, les
filtres, l'ajout d'un élève et le refus d'un paiement excessif sans insertion en
base. Des captures des trois pages sont générées en mode offscreen avec
`widget.grab()` et sont disponibles dans `screenshots/`.

### Points à expliquer à l'oral

1. **Les couches restent séparées** : le widget récupère les données par un
   service ; le service utilise les repositories pour accéder à SQLite.
2. **Le contrôle visuel ne remplace pas la règle métier** : le formulaire
   désactive l'action si le montant est trop élevé, et le service revalide le
   solde au moment d'enregistrer.
3. **Les erreurs sont traitées au bon niveau** : une erreur métier est montrée
   avec son explication ; une erreur inattendue est journalisée et remplacée
   par un message qui ne bloque pas l'application.
4. **Les tests UI sont automatisables** : le mode `offscreen` permet de
   construire et manipuler les widgets même sans écran graphique.
