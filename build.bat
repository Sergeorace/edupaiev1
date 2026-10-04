@echo off
REM Script de build pour Gestion Scolarite (Windows)
REM Ce script installe les dépendances, lance les tests et construit l'exécutable

echo ========================================
echo Gestion Scolarite - Build Script
echo ========================================
echo.

REM Vérifier que Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Erreur: Python n'est pas installé ou pas dans le PATH
    pause
    exit /b 1
)

echo [1/4] Installation des dependances...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Erreur lors de l'installation des dependances
    pause
    exit /b 1
)
echo Dependances installees avec succes
echo.

echo [2/4] Generation de la base de donnees de test...
python -m database.database
if %errorlevel% neq 0 (
    echo Erreur lors de la generation de la base de donnees
    pause
    exit /b 1
)
echo Base de donnees generee avec succes
echo.

echo [3/4] Execution des tests...
python -m pytest tests/ -v
if %errorlevel% neq 0 (
    echo Erreur: Certains tests ont echoue
    echo Le build continue quand meme...
    echo.
)
echo Tests termines
echo.

echo [4/4] Construction de l'executable avec PyInstaller...
python -m pip install pyinstaller
pyinstaller --onefile --windowed gestion_scolarite.spec
if %errorlevel% neq 0 (
    echo Erreur lors de la construction de l'executable
    pause
    exit /b 1
)
echo Executable construit avec succes
echo.

echo ========================================
echo Build termine avec succes!
echo L'executable se trouve dans: dist\GestionScolarite.exe
echo ========================================
pause
