-- Prépare l'année scolaire minimale utilisée par les tests des repositories.
INSERT INTO annees_scolaires (annee, date_debut, date_fin)
VALUES ('2025-2026', '2025-09-01', '2026-07-31');

-- Ajoute la classe de référence utilisée par les tests.
INSERT INTO classes (nom, niveau)
VALUES ('6ème A', 'Collège');

-- Ajoute les lignes de frais nécessaires aux données minimales des tests.
INSERT INTO frais_classe (classe_id, annee_id, type_frais, montant, description)
VALUES
    (1, 1, 'Inscription', 25000, 'Frais d''inscription'),
    (1, 1, 'Scolarité', 150000, 'Frais de scolarité');
