-- Schéma de la base de données pour la gestion de scolarité
-- SGBD : SQLite

-- Table des années scolaires
CREATE TABLE IF NOT EXISTS annees_scolaires (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    annee TEXT NOT NULL UNIQUE,  -- Format : "2025-2026"
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    CHECK (date_fin > date_debut)
);

-- Table des classes
CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL UNIQUE,  -- Ex: "6ème A", "5ème B"
    niveau TEXT NOT NULL  -- Ex: "Primaire", "Collège"
);

-- Table des frais de classe par année scolaire (grille de frais)
CREATE TABLE IF NOT EXISTS frais_classe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    classe_id INTEGER NOT NULL,
    annee_id INTEGER NOT NULL,
    type_frais TEXT NOT NULL,  -- "Inscription", "Scolarité", "Autres"
    montant INTEGER NOT NULL,
    description TEXT,
    FOREIGN KEY (classe_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (annee_id) REFERENCES annees_scolaires(id) ON DELETE CASCADE,
    CHECK (montant > 0),
    UNIQUE (classe_id, annee_id, type_frais)
);

-- Index pour accélérer les recherches de frais par classe et année
CREATE INDEX IF NOT EXISTS idx_frais_classe_annee ON frais_classe(classe_id, annee_id);

-- Table des élèves
CREATE TABLE IF NOT EXISTS eleves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matricule TEXT NOT NULL UNIQUE,  -- Matricule unique
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    date_naissance DATE NOT NULL,
    sexe TEXT NOT NULL CHECK (sexe IN ('M', 'F')),
    classe_id INTEGER NOT NULL,
    tuteur TEXT NOT NULL,
    telephone TEXT NOT NULL,
    actif INTEGER NOT NULL DEFAULT 1,  -- 1 = actif, 0 = archivé
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (classe_id) REFERENCES classes(id),
    CHECK (actif IN (0, 1))
);

-- Index pour accélérer les recherches d'élèves
CREATE INDEX IF NOT EXISTS idx_eleves_classe ON eleves(classe_id);
CREATE INDEX IF NOT EXISTS idx_eleves_actif ON eleves(actif);
CREATE INDEX IF NOT EXISTS idx_eleves_nom ON eleves(nom, prenom);

-- Table des paiements
CREATE TABLE IF NOT EXISTS paiements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    eleve_id INTEGER NOT NULL,
    annee_id INTEGER NOT NULL,
    montant INTEGER NOT NULL,
    date_paiement DATE NOT NULL,
    mode_paiement TEXT NOT NULL,  -- "Espèces", "Chèque", "Virement", "Mobile"
    motif TEXT,
    statut TEXT NOT NULL DEFAULT 'valide',  -- "valide" ou "annule"
    motif_annulation TEXT,
    date_annulation DATE,
    FOREIGN KEY (eleve_id) REFERENCES eleves(id),
    FOREIGN KEY (annee_id) REFERENCES annees_scolaires(id),
    CHECK (montant > 0),
    CHECK (statut IN ('valide', 'annule'))
);

-- Index pour accélérer les recherches de paiements
CREATE INDEX IF NOT EXISTS idx_paiements_eleve ON paiements(eleve_id);
CREATE INDEX IF NOT EXISTS idx_paiements_annee ON paiements(annee_id);
CREATE INDEX IF NOT EXISTS idx_paiements_statut ON paiements(statut);
CREATE INDEX IF NOT EXISTS idx_paiements_eleve_annee ON paiements(eleve_id, annee_id);

-- Table des reçus
CREATE TABLE IF NOT EXISTS recus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero TEXT NOT NULL UNIQUE,  -- Format : "REC-2026-00001"
    paiement_id INTEGER NOT NULL UNIQUE,
    annee_id INTEGER NOT NULL,
    donnees_json TEXT NOT NULL,  -- Données figées du reçu en JSON
    date_generation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paiement_id) REFERENCES paiements(id),
    FOREIGN KEY (annee_id) REFERENCES annees_scolaires(id)
);

-- Index pour accélérer les recherches de reçus
CREATE INDEX IF NOT EXISTS idx_recus_numero ON recus(numero);
CREATE INDEX IF NOT EXISTS idx_recus_paiement ON recus(paiement_id);
CREATE INDEX IF NOT EXISTS idx_recus_annee ON recus(annee_id);
