-- Données de test pour la base de données de gestion de scolarité

-- Insertion d'une année scolaire
INSERT INTO annees_scolaires (annee, date_debut, date_fin)
VALUES ('2025-2026', '2025-09-01', '2026-07-31');

-- Insertion de 4 classes
INSERT INTO classes (nom, niveau) VALUES
('6ème A', 'Collège'),
('6ème B', 'Collège'),
('5ème A', 'Collège'),
('4ème A', 'Collège');

-- Insertion des grilles de frais pour chaque classe (année 2025-2026)
-- Classe 6ème A
INSERT INTO frais_classe (classe_id, annee_id, type_frais, montant, description) VALUES
(1, 1, 'Inscription', 25000, 'Frais d''inscription'),
(1, 1, 'Scolarité', 150000, 'Frais de scolarité annuels'),
(1, 1, 'Autres', 10000, 'Frais de matériel');

-- Classe 6ème B
INSERT INTO frais_classe (classe_id, annee_id, type_frais, montant, description) VALUES
(2, 1, 'Inscription', 25000, 'Frais d''inscription'),
(2, 1, 'Scolarité', 150000, 'Frais de scolarité annuels'),
(2, 1, 'Autres', 10000, 'Frais de matériel');

-- Classe 5ème A
INSERT INTO frais_classe (classe_id, annee_id, type_frais, montant, description) VALUES
(3, 1, 'Inscription', 30000, 'Frais d''inscription'),
(3, 1, 'Scolarité', 175000, 'Frais de scolarité annuels'),
(3, 1, 'Autres', 15000, 'Frais de matériel');

-- Classe 4ème A
INSERT INTO frais_classe (classe_id, annee_id, type_frais, montant, description) VALUES
(4, 1, 'Inscription', 35000, 'Frais d''inscription'),
(4, 1, 'Scolarité', 200000, 'Frais de scolarité annuels'),
(4, 1, 'Autres', 20000, 'Frais de matériel');

-- Insertion de 20 élèves
INSERT INTO eleves (matricule, nom, prenom, date_naissance, sexe, classe_id, tuteur, telephone, actif) VALUES
('MAT001', 'KOUASSI', 'Jean', '2012-05-15', 'M', 1, 'KOUASSI Paul', '0707010101', 1),
('MAT002', 'DIALLO', 'Aminata', '2012-08-22', 'F', 1, 'DIALLO Ibrahim', '0707010102', 1),
('MAT003', 'KONÉ', 'Moussa', '2013-02-10', 'M', 1, 'KONÉ Sékou', '0707010103', 1),
('MAT004', 'TOURÉ', 'Fatou', '2012-11-30', 'F', 1, 'TOURÉ Mamadou', '0707010104', 1),
('MAT005', 'BAKAYOKO', 'Yao', '2013-04-18', 'M', 1, 'BAKAYOKO Koffi', '0707010105', 1),
('MAT006', 'COULIBALY', 'Aïcha', '2012-09-25', 'F', 2, 'COULIBALY Adama', '0707010106', 1),
('MAT007', 'TRAORÉ', 'Ousmane', '2013-01-12', 'M', 2, 'TRAORÉ Cheick', '0707010107', 1),
('MAT008', 'YÉO', 'Mariam', '2012-06-08', 'F', 2, 'YÉO Dramane', '0707010108', 1),
('MAT009', 'GBÉKOUÉ', 'Kouamé', '2013-03-20', 'M', 2, 'GBÉKOUÉ Kouamé', '0707010109', 1),
('MAT010', 'N''GUESSAN', 'Adjoua', '2012-12-05', 'F', 2, 'N''GUESSAN Yao', '0707010110', 1),
('MAT011', 'KOFFI', 'Emmanuel', '2011-07-14', 'M', 3, 'KOFFI Augustin', '0707010111', 1),
('MAT012', 'DJÉDJÉ', 'Cécile', '2011-10-28', 'F', 3, 'DJÉDJÉ Jean', '0707010112', 1),
('MAT013', 'SANGARÉ', 'Baba', '2012-02-16', 'M', 3, 'SANGARÉ Mahamadou', '0707010113', 1),
('MAT014', 'DOSSO', 'Clarisse', '2011-05-03', 'F', 3, 'DOSSO Pierre', '0707010114', 1),
('MAT015', 'COULIBALY', 'Ibrahim', '2012-08-19', 'M', 3, 'COULIBALY Lassana', '0707010115', 1),
('MAT016', 'BAMBA', 'Sita', '2010-04-11', 'F', 4, 'BAMBA Moriba', '0707010116', 1),
('MAT017', 'CAMARA', 'Sidy', '2011-09-27', 'M', 4, 'CAMARA Ismaël', '0707010117', 1),
('MAT018', 'FOFANA', 'Fatim', '2010-12-15', 'F', 4, 'FOFANA Mamadou', '0707010118', 1),
('MAT019', 'KÉRÉ', 'Christian', '2011-06-02', 'M', 4, 'KÉRÉ Mathieu', '0707010119', 1),
('MAT020', 'ZÉNOU', 'Ramatou', '2010-11-08', 'F', 4, 'ZÉNOU Thomas', '0707010120', 1);

-- Insertion de 40 paiements (couvrant les 3 statuts et 2 annulations)
-- Élèves IMPAYÉS (aucun paiement) : MAT011, MAT016, MAT019 (3 élèves)

-- Élèves PARTIELLEMENT PAYÉS (0 < payé < dû)
-- MAT001 : Total dû = 185000, Payé = 100000
INSERT INTO paiements (eleve_id, annee_id, montant, date_paiement, mode_paiement, motif, statut) VALUES
(1, 1, 50000, '2025-09-15', 'Espèces', '1ère tranche', 'valide'),
(1, 1, 50000, '2025-10-20', 'Espèces', '2ème tranche', 'valide');

-- MAT002 : Total dû = 185000, Payé = 75000
INSERT INTO paiements (eleve_id, annee_id, montant, date_paiement, mode_paiement, motif, statut) VALUES
(2, 1, 50000, '2025-09-10', 'Espèces', 'Inscription', 'valide'),
(2, 1, 25000, '2025-10-05', 'Mobile', 'Acompte', 'valide');

-- MAT003 : Total dû = 185000, Payé = 150000
INSERT INTO paiements (eleve_id, annee_id, montant, date_paiement, mode_paiement, motif, statut) VALUES
(3, 1, 25000, '2025-09-12', 'Espèces', 'Inscription', 'valide'),
(3, 1, 75000, '2025-10-01', 'Virement', 'Scolarité', 'valide'),
(3, 1, 50000, '2025-11-15', 'Espèces', '3ème tranche', 'valide');

-- MAT004 : Total dû = 185000, Payé = 50000
INSERT INTO paiements (eleve_id, annee_id, montant, date_paiement, mode_paiement, motif, statut) VALUES
(4, 1, 50000, '2025-09-20', 'Chèque', 'Inscription', 'valide');

-- MAT006 : Total dû = 185000, Payé = 100000
INSERT INTO paiements (eleve_id, annee_id, montant, date_paiement, mode_paiement, motif, statut) VALUES
(6, 1, 50000, '2025-09-18', 'Espèces', '1ère tranche', 'valide'),
(6, 1, 50000, '2025-10-25', 'Espèces', '2ème tranche', 'valide');

-- MAT007 : Total dû = 185000, Payé = 120000
INSERT INTO paiements (eleve_id, annee_id, montant, date_paiement, mode_paiement, motif, statut) VALUES
(7, 1, 25000, '2025-09-14', 'Espèces', 'Inscription', 'valide'),
(7, 1, 95000, '2025-10-10', 'Virement', 'Scolarité partielle', 'valide');

-- MAT008 : Total dû = 185000, Payé = 60000
INSERT INTO paiements (eleve_id, annee_id, montant, date_paiement, mode_paiement, motif, statut) VALUES
(8, 1, 60000, '2025-09-22', 'Mobile', 'Paiement mobile', 'valide');

-- MAT009 : Total dû = 185000, Payé = 90000
INSERT INTO paiements (eleve_id, annee_id, montant, date_paiement, mode_paiement, motif, statut) VALUES
(9, 1, 50000, '2025-09-16', 'Espèces', '1ère tranche', 'valide'),
(9, 1, 40000, '2025-10-12', 'Espèces', '2ème tranche', 'valide');

-- MAT012 : Total dû = 220000, Payé = 150000
INSERT INTO paiements (eleve_id, annee_id, montant, date_paiement, mode_paiement, motif, statut) VALUES
(12, 1, 30000, '2025-09-13', 'Espèces', 'Inscription', 'valide'),
(12, 1, 120000, '2025-10-08', 'Virement', 'Scolarité partielle', 'valide');

-- MAT013 : Total dû = 220000, Payé = 80000
INSERT INTO paiements (eleve_id, annee_id, montant, date_paiement, mode_paiement, motif, statut) VALUES
(13, 1, 80000, '2025-09-25', 'Espèces', 'Acompte', 'valide');

-- MAT015 : Total dû = 220000, Payé = 175000
INSERT INTO paiements (eleve_id, annee_id, montant, date_paiement, mode_paiement, motif, statut) VALUES
(15, 1, 30000, '2025-09-11', 'Espèces', 'Inscription', 'valide'),
(15, 1, 100000, '2025-10-02', 'Virement', 'Scolarité', 'valide'),
(15, 1, 45000, '2025-11-20', 'Espèces', '3ème tranche', 'valide');

-- MAT017 : Total dû = 255000, Payé = 100000
INSERT INTO paiements (eleve_id, annee_id, montant, date_paiement, mode_paiement, motif, statut) VALUES
(17, 1, 35000, '2025-09-17', 'Espèces', 'Inscription', 'valide'),
(17, 1, 65000, '2025-10-15', 'Espèces', 'Scolarité partielle', 'valide');

-- MAT018 : Total dû = 255000, Payé = 150000
INSERT INTO paiements (eleve_id, annee_id, montant, date_paiement, mode_paiement, motif, statut) VALUES
(18, 1, 35000, '2025-09-19', 'Espèces', 'Inscription', 'valide'),
(18, 1, 115000, '2025-10-18', 'Virement', 'Scolarité partielle', 'valide');

-- MAT020 : Total dû = 255000, Payé = 80000
INSERT INTO paiements (eleve_id, annee_id, montant, date_paiement, mode_paiement, motif, statut) VALUES
(20, 1, 80000, '2025-09-21', 'Mobile', 'Paiement mobile', 'valide');

-- Élèves PAYÉS EN ENTIER (solde = 0)
-- MAT005 : Total dû = 185000, Payé = 185000
INSERT INTO paiements (eleve_id, annee_id, montant, date_paiement, mode_paiement, motif, statut) VALUES
(5, 1, 25000, '2025-09-15', 'Espèces', 'Inscription', 'valide'),
(5, 1, 150000, '2025-10-01', 'Virement', 'Scolarité', 'valide'),
(5, 1, 10000, '2025-11-10', 'Espèces', 'Matériel', 'valide');

-- MAT010 : Total dû = 185000, Payé = 185000
INSERT INTO paiements (eleve_id, annee_id, montant, date_paiement, mode_paiement, motif, statut) VALUES
(10, 1, 50000, '2025-09-14', 'Espèces', '1ère tranche', 'valide'),
(10, 1, 100000, '2025-10-10', 'Virement', 'Scolarité', 'valide'),
(10, 1, 35000, '2025-11-05', 'Espèces', 'Solde', 'valide');

-- MAT014 : Total dû = 220000, Payé = 220000
INSERT INTO paiements (eleve_id, annee_id, montant, date_paiement, mode_paiement, motif, statut) VALUES
(14, 1, 30000, '2025-09-12', 'Espèces', 'Inscription', 'valide'),
(14, 1, 175000, '2025-10-05', 'Virement', 'Scolarité', 'valide'),
(14, 1, 15000, '2025-11-15', 'Espèces', 'Matériel', 'valide');

-- Paiements ANNULÉS (2 paiements annulés)
-- Paiement de MAT002 annulé
INSERT INTO paiements (eleve_id, annee_id, montant, date_paiement, mode_paiement, motif, statut, motif_annulation, date_annulation) VALUES
(2, 1, 30000, '2025-09-25', 'Espèces', 'Annulé par erreur', 'annule', 'Erreur de saisie', '2025-09-26');

-- Paiement de MAT007 annulé
INSERT INTO paiements (eleve_id, annee_id, montant, date_paiement, mode_paiement, motif, statut, motif_annulation, date_annulation) VALUES
(7, 1, 50000, '2025-10-22', 'Espèces', 'Annulé pour doublon', 'annule', 'Doublon de paiement', '2025-10-23');

-- Insertion des reçus pour tous les paiements valides
-- Reçus pour MAT001
INSERT INTO recus (numero, paiement_id, annee_id, donnees_json) VALUES
('REC-2026-00001', 1, 1, '{"nom": "KOUASSI Jean", "classe": "6ème A", "montant": 50000, "total_paye": 50000, "solde": 135000, "date_paiement": "2025-09-15"}'),
('REC-2026-00002', 2, 1, '{"nom": "KOUASSI Jean", "classe": "6ème A", "montant": 50000, "total_paye": 100000, "solde": 85000, "date_paiement": "2025-10-20"}');

-- Reçus pour MAT002
INSERT INTO recus (numero, paiement_id, annee_id, donnees_json) VALUES
('REC-2026-00003', 3, 1, '{"nom": "DIALLO Aminata", "classe": "6ème A", "montant": 50000, "total_paye": 50000, "solde": 135000, "date_paiement": "2025-09-10"}'),
('REC-2026-00004', 4, 1, '{"nom": "DIALLO Aminata", "classe": "6ème A", "montant": 25000, "total_paye": 75000, "solde": 110000, "date_paiement": "2025-10-05"}');

-- Reçus pour MAT003
INSERT INTO recus (numero, paiement_id, annee_id, donnees_json) VALUES
('REC-2026-00005', 5, 1, '{"nom": "KONÉ Moussa", "classe": "6ème A", "montant": 25000, "total_paye": 25000, "solde": 160000, "date_paiement": "2025-09-12"}'),
('REC-2026-00006', 6, 1, '{"nom": "KONÉ Moussa", "classe": "6ème A", "montant": 75000, "total_paye": 100000, "solde": 85000, "date_paiement": "2025-10-01"}'),
('REC-2026-00007', 7, 1, '{"nom": "KONÉ Moussa", "classe": "6ème A", "montant": 50000, "total_paye": 150000, "solde": 35000, "date_paiement": "2025-11-15"}');

-- Reçus pour MAT004
INSERT INTO recus (numero, paiement_id, annee_id, donnees_json) VALUES
('REC-2026-00008', 8, 1, '{"nom": "TOURÉ Fatou", "classe": "6ème A", "montant": 50000, "total_paye": 50000, "solde": 135000, "date_paiement": "2025-09-20"}');

-- Reçus pour MAT005
INSERT INTO recus (numero, paiement_id, annee_id, donnees_json) VALUES
('REC-2026-00009', 9, 1, '{"nom": "BAKAYOKO Yao", "classe": "6ème A", "montant": 25000, "total_paye": 25000, "solde": 160000, "date_paiement": "2025-09-15"}'),
('REC-2026-00010', 10, 1, '{"nom": "BAKAYOKO Yao", "classe": "6ème A", "montant": 150000, "total_paye": 175000, "solde": 10000, "date_paiement": "2025-10-01"}'),
('REC-2026-00011', 11, 1, '{"nom": "BAKAYOKO Yao", "classe": "6ème A", "montant": 10000, "total_paye": 185000, "solde": 0, "date_paiement": "2025-11-10"}');

-- Reçus pour MAT006
INSERT INTO recus (numero, paiement_id, annee_id, donnees_json) VALUES
('REC-2026-00012', 12, 1, '{"nom": "COULIBALY Aïcha", "classe": "6ème B", "montant": 50000, "total_paye": 50000, "solde": 135000, "date_paiement": "2025-09-18"}'),
('REC-2026-00013', 13, 1, '{"nom": "COULIBALY Aïcha", "classe": "6ème B", "montant": 50000, "total_paye": 100000, "solde": 85000, "date_paiement": "2025-10-25"}');

-- Reçus pour MAT007
INSERT INTO recus (numero, paiement_id, annee_id, donnees_json) VALUES
('REC-2026-00014', 14, 1, '{"nom": "TRAORÉ Ousmane", "classe": "6ème B", "montant": 25000, "total_paye": 25000, "solde": 160000, "date_paiement": "2025-09-14"}'),
('REC-2026-00015', 15, 1, '{"nom": "TRAORÉ Ousmane", "classe": "6ème B", "montant": 95000, "total_paye": 120000, "solde": 65000, "date_paiement": "2025-10-10"}');

-- Reçus pour MAT008
INSERT INTO recus (numero, paiement_id, annee_id, donnees_json) VALUES
('REC-2026-00016', 16, 1, '{"nom": "YÉO Mariam", "classe": "6ème B", "montant": 60000, "total_paye": 60000, "solde": 125000, "date_paiement": "2025-09-22"}');

-- Reçus pour MAT009
INSERT INTO recus (numero, paiement_id, annee_id, donnees_json) VALUES
('REC-2026-00017', 17, 1, '{"nom": "GBÉKOUÉ Kouamé", "classe": "6ème B", "montant": 50000, "total_paye": 50000, "solde": 135000, "date_paiement": "2025-09-16"}'),
('REC-2026-00018', 18, 1, '{"nom": "GBÉKOUÉ Kouamé", "classe": "6ème B", "montant": 40000, "total_paye": 90000, "solde": 95000, "date_paiement": "2025-10-12"}');

-- Reçus pour MAT010
INSERT INTO recus (numero, paiement_id, annee_id, donnees_json) VALUES
('REC-2026-00019', 19, 1, '{"nom": "N''GUESSAN Adjoua", "classe": "6ème B", "montant": 50000, "total_paye": 50000, "solde": 135000, "date_paiement": "2025-09-14"}'),
('REC-2026-00020', 20, 1, '{"nom": "N''GUESSAN Adjoua", "classe": "6ème B", "montant": 100000, "total_paye": 150000, "solde": 35000, "date_paiement": "2025-10-10"}'),
('REC-2026-00021', 21, 1, '{"nom": "N''GUESSAN Adjoua", "classe": "6ème B", "montant": 35000, "total_paye": 185000, "solde": 0, "date_paiement": "2025-11-05"}');

-- Reçus pour MAT012
INSERT INTO recus (numero, paiement_id, annee_id, donnees_json) VALUES
('REC-2026-00022', 22, 1, '{"nom": "DJÉDJÉ Cécile", "classe": "5ème A", "montant": 30000, "total_paye": 30000, "solde": 190000, "date_paiement": "2025-09-13"}'),
('REC-2026-00023', 23, 1, '{"nom": "DJÉDJÉ Cécile", "classe": "5ème A", "montant": 120000, "total_paye": 150000, "solde": 70000, "date_paiement": "2025-10-08"}');

-- Reçus pour MAT013
INSERT INTO recus (numero, paiement_id, annee_id, donnees_json) VALUES
('REC-2026-00024', 24, 1, '{"nom": "SANGARÉ Baba", "classe": "5ème A", "montant": 80000, "total_paye": 80000, "solde": 140000, "date_paiement": "2025-09-25"}');

-- Reçus pour MAT014
INSERT INTO recus (numero, paiement_id, annee_id, donnees_json) VALUES
('REC-2026-00025', 25, 1, '{"nom": "DOSSO Clarisse", "classe": "5ème A", "montant": 30000, "total_paye": 30000, "solde": 190000, "date_paiement": "2025-09-12"}'),
('REC-2026-00026', 26, 1, '{"nom": "DOSSO Clarisse", "classe": "5ème A", "montant": 175000, "total_paye": 205000, "solde": 15000, "date_paiement": "2025-10-05"}'),
('REC-2026-00027', 27, 1, '{"nom": "DOSSO Clarisse", "classe": "5ème A", "montant": 15000, "total_paye": 220000, "solde": 0, "date_paiement": "2025-11-15"}');

-- Reçus pour MAT015
INSERT INTO recus (numero, paiement_id, annee_id, donnees_json) VALUES
('REC-2026-00028', 28, 1, '{"nom": "COULIBALY Ibrahim", "classe": "5ème A", "montant": 30000, "total_paye": 30000, "solde": 190000, "date_paiement": "2025-09-11"}'),
('REC-2026-00029', 29, 1, '{"nom": "COULIBALY Ibrahim", "classe": "5ème A", "montant": 100000, "total_paye": 130000, "solde": 90000, "date_paiement": "2025-10-02"}'),
('REC-2026-00030', 30, 1, '{"nom": "COULIBALY Ibrahim", "classe": "5ème A", "montant": 45000, "total_paye": 175000, "solde": 45000, "date_paiement": "2025-11-20"}');

-- Reçus pour MAT017
INSERT INTO recus (numero, paiement_id, annee_id, donnees_json) VALUES
('REC-2026-00031', 31, 1, '{"nom": "CAMARA Sidy", "classe": "4ème A", "montant": 35000, "total_paye": 35000, "solde": 220000, "date_paiement": "2025-09-17"}'),
('REC-2026-00032', 32, 1, '{"nom": "CAMARA Sidy", "classe": "4ème A", "montant": 65000, "total_paye": 100000, "solde": 155000, "date_paiement": "2025-10-15"}');

-- Reçus pour MAT018
INSERT INTO recus (numero, paiement_id, annee_id, donnees_json) VALUES
('REC-2026-00033', 33, 1, '{"nom": "FOFANA Fatim", "classe": "4ème A", "montant": 35000, "total_paye": 35000, "solde": 220000, "date_paiement": "2025-09-19"}'),
('REC-2026-00034', 34, 1, '{"nom": "FOFANA Fatim", "classe": "4ème A", "montant": 115000, "total_paye": 150000, "solde": 105000, "date_paiement": "2025-10-18"}');

-- Reçus pour MAT020
INSERT INTO recus (numero, paiement_id, annee_id, donnees_json) VALUES
('REC-2026-00035', 35, 1, '{"nom": "ZÉNOU Ramatou", "classe": "4ème A", "montant": 80000, "total_paye": 80000, "solde": 175000, "date_paiement": "2025-09-21"}');

-- Reçus pour les paiements annulés (restent consultables)
INSERT INTO recus (numero, paiement_id, annee_id, donnees_json) VALUES
('REC-2026-00036', 36, 1, '{"nom": "DIALLO Aminata", "classe": "6ème A", "montant": 30000, "total_paye": 105000, "solde": 80000, "date_paiement": "2025-09-25"}'),
('REC-2026-00037', 37, 1, '{"nom": "TRAORÉ Ousmane", "classe": "6ème B", "montant": 50000, "total_paye": 170000, "solde": 15000, "date_paiement": "2025-10-22"}');
