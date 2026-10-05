# Polices pour Edupaie

Ce dossier doit contenir les fichiers de police suivants :

## Poppins
- Poppins-SemiBold.ttf
- Poppins-Bold.ttf
- Poppins-ExtraBold.ttf

## Inter
- Inter-Regular.ttf
- Inter-Medium.ttf
- Inter-SemiBold.ttf

## Comment obtenir ces polices

### Option 1 : Google Fonts
1. Allez sur https://fonts.google.com/
2. Téléchargez Poppins (SemiBold, Bold, ExtraBold)
3. Téléchargez Inter (Regular, Medium, SemiBold)
4. Placez les fichiers .ttf dans ce dossier

### Option 2 : Utiliser les polices système
Si vous ne voulez pas embarquer les polices, l'application utilisera automatiquement "Segoe UI" comme police de repli sur Windows.

## Note pour PyInstaller
Si vous utilisez PyInstaller, assurez-vous d'ajouter ce dossier avec --add-data "resources/fonts;resources/fonts" dans votre commande de build.
