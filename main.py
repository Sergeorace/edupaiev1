"""
Point d'entrée principal de l'application.
"""

if __name__ == "__main__":
    # TODO: Initialiser l'interface PySide6 (étapes ultérieures)
    print("Application Gestion Scolarité")
    print("Initialisation de la base de données...")
    from database.database import init_database

    init_database()
    print("Base de données initialisée avec succès.")
