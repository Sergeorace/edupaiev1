"""
Générateur de PDF pour les reçus de paiement.
Utilise reportlab pour créer des PDF à partir des données figées stockées dans la table recus.
"""

import json
from pathlib import Path
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


# Nom de l'établissement (configuration)
ETABLISSEMENT_NOM = "ÉCOLE EXEMPLE"
ETABLISSEMENT_ADRESSE = "123 Rue de l'École"
ETABLISSEMENT_VILLE = "Abidjan, Côte d'Ivoire"
ETABLISSEMENT_TEL = "+225 01 02 03 04 05"


def register_fonts() -> None:
    """
    Enregistre les polices pour le PDF.
    Utilise Helvetica (standard) pour éviter les dépendances externes.
    """
    # Helvetica est une police standard disponible dans reportlab
    # Pas besoin d'enregistrer des polices personnalisées
    pass


def generer_pdf_recu(
    donnees_json: str,
    numero_recu: str,
    date_generation: str,
    statut_paiement: str = "valide",
    output_path: Optional[Path] = None,
) -> Path:
    """
    Génère un PDF de reçu à partir des données figées.

    Args:
        donnees_json: Données figées du reçu en JSON.
        numero_recu: Numéro du reçu.
        date_generation: Date de génération du reçu.
        statut_paiement: Statut du paiement ("valide" ou "annulé").
        output_path: Chemin de sortie du PDF. Si None, génère dans le dossier temporaire.

    Returns:
        Chemin du fichier PDF généré.
    """
    # Parser les données JSON
    donnees = json.loads(donnees_json)

    # Définir le chemin de sortie
    if output_path is None:
        output_path = Path.home() / "Desktop" / f"recu_{numero_recu}.pdf"

    # Créer le document PDF
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    # Créer les éléments du document
    elements = []
    styles = getSampleStyleSheet()

    # En-tête de l'établissement
    elements.append(Spacer(1, 1 * cm))

    header_data = [
        [ETABLISSEMENT_NOM],
        [ETABLISSEMENT_ADRESSE],
        [f"{ETABLISSEMENT_VILLE} - Tél: {ETABLISSEMENT_TEL}"],
    ]

    header_table = Table(header_data, colWidths=[15 * cm])
    header_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (0, 2), "CENTER"),
                ("FONTNAME", (0, 0), (0, 2), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (0, 0), 18),
                ("FONTSIZE", (0, 1), (0, 2), 10),
                ("TEXTCOLOR", (0, 0), (0, 2), colors.darkblue),
            ]
        )
    )
    elements.append(header_table)

    elements.append(Spacer(1, 1.5 * cm))

    # Titre "REÇU DE PAIEMENT"
    titre = Paragraph("REÇU DE PAIEMENT", styles["Heading1"])
    titre.hAlign = "CENTER"
    elements.append(titre)

    elements.append(Spacer(1, 0.5 * cm))

    # Numéro et date du reçu
    info_recu_data = [
        [f"Numéro : {numero_recu}", f"Date : {date_generation}"],
    ]

    info_recu_table = Table(info_recu_data, colWidths=[7.5 * cm, 7.5 * cm])
    info_recu_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (1, 0), "CENTER"),
                ("FONTNAME", (0, 0), (1, 0), "Helvetica"),
                ("FONTSIZE", (0, 0), (1, 0), 11),
                ("BOTTOMPADDING", (0, 0), (1, 0), 10),
            ]
        )
    )
    elements.append(info_recu_table)

    elements.append(Spacer(1, 1 * cm))

    # Ligne de séparation
    elements.append(Spacer(1, 0.2 * cm))

    # Informations de l'élève et du paiement
    paiement_data = [
        ["Élève :", donnees.get("nom", "")],
        ["Classe :", donnees.get("classe", "")],
        ["Montant payé :", f"{donnees.get('montant', 0):,} FCFA".replace(",", " ")],
        ["Total payé à ce jour :", f"{donnees.get('total_paye', 0):,} FCFA".replace(",", " ")],
        ["Solde restant :", f"{donnees.get('solde', 0):,} FCFA".replace(",", " ")],
        ["Date du paiement :", donnees.get("date_paiement", "")],
    ]

    paiement_table = Table(paiement_data, colWidths=[5 * cm, 10 * cm])
    paiement_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (0, 6), "LEFT"),
                ("ALIGN", (1, 0), (1, 6), "LEFT"),
                ("FONTNAME", (0, 0), (0, 6), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, 6), "Helvetica"),
                ("FONTSIZE", (0, 0), (1, 6), 11),
                ("BOTTOMPADDING", (0, 0), (1, 6), 8),
                ("BACKGROUND", (0, 0), (0, 6), colors.lightgrey),
            ]
        )
    )
    elements.append(paiement_table)

    elements.append(Spacer(1, 1.5 * cm))

    # Mode de paiement
    mode_paiement = donnees.get("mode_paiement", "Non spécifié")
    mode_text = Paragraph(f"<b>Mode de paiement :</b> {mode_paiement}", styles["Normal"])
    elements.append(mode_text)

    elements.append(Spacer(1, 2 * cm))

    # Pied de page
    pied_data = [
        ["Signature du comptable", "Signature du responsable"],
        ["", ""],
        ["", ""],
    ]

    pied_table = Table(pied_data, colWidths=[7.5 * cm, 7.5 * cm])
    pied_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (1, 0), "CENTER"),
                ("FONTNAME", (0, 0), (1, 0), "Helvetica-Oblique"),
                ("FONTSIZE", (0, 0), (1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (1, 0), 15),
                ("LINEBELOW", (0, 0), (1, 0), 1, colors.black),
            ]
        )
    )
    elements.append(pied_table)

    # Ajouter le filigrane "ANNULÉ" si le paiement est annulé
    if statut_paiement == "annulé":
        watermark = Paragraph(
            "<font size=40 color=red><b>ANNULÉ</b></font>", styles["Normal"]
        )
        # Le filigrane sera ajouté lors de la construction du canvas
        doc.build(elements, onFirstPage=lambda canvas, doc: _add_watermark(canvas, "ANNULÉ"))
    else:
        doc.build(elements)

    return output_path


def _add_watermark(canvas: canvas.Canvas, text: str) -> None:
    """
    Ajoute un filigrane au PDF.

    Args:
        canvas: Canvas reportlab.
        text: Texte du filigrane.
    """
    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 80)
    canvas.setFillColorRGB(0.9, 0.9, 0.9)  # Gris clair
    canvas.translate(A4[0] / 2, A4[1] / 2)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, text)
    canvas.restoreState()


if __name__ == "__main__":
    # Test du générateur
    test_donnees = {
        "nom": "KOUASSI Jean",
        "classe": "6ème A",
        "montant": 50000,
        "total_paye": 100000,
        "solde": 85000,
        "date_paiement": "2025-09-15",
        "mode_paiement": "Espèces",
    }

    output = generer_pdf_recu(
        json.dumps(test_donnees),
        "REC-2026-00001",
        "2025-09-15 10:30:00",
        "valide",
    )
    print(f"PDF généré : {output}")
