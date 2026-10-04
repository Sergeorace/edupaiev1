"""
Repository pour la gestion des élèves.
"""

import sqlite3
from typing import List, Optional
from models.eleve import Eleve


class EleveRepository:
    """Repository pour les opérations CRUD sur les élèves."""

    def __init__(self, conn: sqlite3.Connection):
        """
        Initialise le repository avec une connexion.

        Args:
            conn: Connexion SQLite à utiliser.
        """
        self.conn = conn

    def create(self, eleve: Eleve) -> Eleve:
        """
        Crée un nouvel élève dans la base de données.

        Args:
            eleve: L'élève à créer (sans l'ID).

        Returns:
            L'élève créé avec son ID généré.
        """
        # Insertion de l'élève
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO eleves (matricule, nom, prenom, date_naissance, sexe,
                               classe_id, tuteur, telephone, actif)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                eleve.matricule,
                eleve.nom,
                eleve.prenom,
                eleve.date_naissance,
                eleve.sexe,
                eleve.classe_id,
                eleve.tuteur,
                eleve.telephone,
                1 if eleve.actif else 0,
            ),
        )
        eleve.id = cursor.lastrowid
        return eleve

    def get_by_id(self, eleve_id: int) -> Optional[Eleve]:
        """
        Récupère un élève par son ID.

        Args:
            eleve_id: ID de l'élève.

        Returns:
            L'élève trouvé ou None.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT e.id, e.matricule, e.nom, e.prenom, e.date_naissance, e.sexe,
                   e.classe_id, c.nom as classe_nom, e.tuteur, e.telephone,
                   e.actif, e.date_creation
            FROM eleves e
            LEFT JOIN classes c ON e.classe_id = c.id
            WHERE e.id = ?
            """,
            (eleve_id,),
        )
        row = cursor.fetchone()
        if row:
            return self._row_to_eleve(row)
        return None

    def get_by_matricule(self, matricule: str) -> Optional[Eleve]:
        """
        Récupère un élève par son matricule.

        Args:
            matricule: Matricule de l'élève.

        Returns:
            L'élève trouvé ou None.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT e.id, e.matricule, e.nom, e.prenom, e.date_naissance, e.sexe,
                   e.classe_id, c.nom as classe_nom, e.tuteur, e.telephone,
                   e.actif, e.date_creation
            FROM eleves e
            LEFT JOIN classes c ON e.classe_id = c.id
            WHERE e.matricule = ?
            """,
            (matricule,),
        )
        row = cursor.fetchone()
        if row:
            return self._row_to_eleve(row)
        return None

    def get_all(self, actif_only: bool = True) -> List[Eleve]:
        """
        Récupère tous les élèves.

        Args:
            actif_only: Si True, ne retourne que les élèves actifs.

        Returns:
            Liste des élèves.
        """
        cursor = self.conn.cursor()
        if actif_only:
            cursor.execute(
                """
                SELECT e.id, e.matricule, e.nom, e.prenom, e.date_naissance, e.sexe,
                       e.classe_id, c.nom as classe_nom, e.tuteur, e.telephone,
                       e.actif, e.date_creation
                FROM eleves e
                LEFT JOIN classes c ON e.classe_id = c.id
                WHERE e.actif = 1
                ORDER BY e.nom, e.prenom
                """
            )
        else:
            cursor.execute(
                """
                SELECT e.id, e.matricule, e.nom, e.prenom, e.date_naissance, e.sexe,
                       e.classe_id, c.nom as classe_nom, e.tuteur, e.telephone,
                       e.actif, e.date_creation
                FROM eleves e
                LEFT JOIN classes c ON e.classe_id = c.id
                ORDER BY e.nom, e.prenom
                """
            )
        return [self._row_to_eleve(row) for row in cursor.fetchall()]

    def search(
        self,
        nom: Optional[str] = None,
        prenom: Optional[str] = None,
        matricule: Optional[str] = None,
        classe_id: Optional[int] = None,
        actif_only: bool = True,
    ) -> List[Eleve]:
        """
        Recherche des élèves selon différents critères.

        Args:
            nom: Nom de l'élève (recherche partielle).
            prenom: Prénom de l'élève (recherche partielle).
            matricule: Matricule de l'élève (recherche partielle).
            classe_id: ID de la classe.
            actif_only: Si True, ne retourne que les élèves actifs.

        Returns:
            Liste des élèves correspondant aux critères.
        """
        query = """
            SELECT e.id, e.matricule, e.nom, e.prenom, e.date_naissance, e.sexe,
                   e.classe_id, c.nom as classe_nom, e.tuteur, e.telephone,
                   e.actif, e.date_creation
            FROM eleves e
            LEFT JOIN classes c ON e.classe_id = c.id
            WHERE 1=1
        """
        params = []

        if actif_only:
            query += " AND e.actif = 1"

        if nom:
            query += " AND e.nom LIKE ?"
            params.append(f"%{nom}%")

        if prenom:
            query += " AND e.prenom LIKE ?"
            params.append(f"%{prenom}%")

        if matricule:
            query += " AND e.matricule LIKE ?"
            params.append(f"%{matricule}%")

        if classe_id:
            query += " AND e.classe_id = ?"
            params.append(classe_id)

        query += " ORDER BY e.nom, e.prenom"

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return [self._row_to_eleve(row) for row in cursor.fetchall()]

    def update(self, eleve: Eleve) -> None:
        """
        Met à jour un élève existant.

        Args:
            eleve: L'élève à mettre à jour (avec l'ID).
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE eleves
            SET matricule = ?, nom = ?, prenom = ?, date_naissance = ?,
                sexe = ?, classe_id = ?, tuteur = ?, telephone = ?, actif = ?
            WHERE id = ?
            """,
            (
                eleve.matricule,
                eleve.nom,
                eleve.prenom,
                eleve.date_naissance,
                eleve.sexe,
                eleve.classe_id,
                eleve.tuteur,
                eleve.telephone,
                1 if eleve.actif else 0,
                eleve.id,
            ),
        )

    def archive(self, eleve_id: int) -> None:
        """
        Archive un élève (met actif = 0).

        Args:
            eleve_id: ID de l'élève à archiver.
        """
        cursor = self.conn.cursor()
        cursor.execute("UPDATE eleves SET actif = 0 WHERE id = ?", (eleve_id,))

    def delete(self, eleve_id: int) -> None:
        """
        Supprime un élève de la base de données.
        Note: Cette méthode ne devrait pas être utilisée selon les règles métier.
        Préférer archive().

        Args:
            eleve_id: ID de l'élève à supprimer.
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM eleves WHERE id = ?", (eleve_id,))

    def _row_to_eleve(self, row: sqlite3.Row) -> Eleve:
        """
        Convertit une ligne de résultat en objet Eleve.

        Args:
            row: Ligne de résultat SQLite.

        Returns:
            Objet Eleve.
        """
        return Eleve(
            id=row["id"],
            matricule=row["matricule"],
            nom=row["nom"],
            prenom=row["prenom"],
            date_naissance=row["date_naissance"],
            sexe=row["sexe"],
            classe_id=row["classe_id"],
            classe_nom=row["classe_nom"],
            tuteur=row["tuteur"],
            telephone=row["telephone"],
            actif=bool(row["actif"]),
            date_creation=row["date_creation"],
        )
