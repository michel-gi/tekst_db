#!/usr/bin/env python3
"""
Een voorbeeldprogramma dat de TextDatabase class gebruikt om een rapport te maken.

Dit script kan worden aangeroepen met command-line argumenten om te specificeren
welk databasebestand en welk item moeten worden gebruikt.
"""

import argparse
import sys

# We importeren alleen de TextDatabase class uit de 'database' module.
from database import TextDatabase


def maak_rapport(bestandsnaam, index_to_get):
    """
    Laadt een database, haalt een specifiek item op en rapporteert de status.

    Args:
        bestandsnaam (str): Het pad naar het databasebestand.
        index_to_get (int): Het indexnummer van het item om op te halen.
    """
    print("--- Start van het rapportageprogramma ---")

    try:
        # Maak een object van de TextDatabase class.
        # De __init__ methode wordt hier aangeroepen en het bestand wordt geladen.
        db = TextDatabase(bestandsnaam)
    except FileNotFoundError:
        print(f"Fout: Het databasebestand '{bestandsnaam}' is niet gevonden.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Fout: Kon de database niet laden. Details: {e}", file=sys.stderr)
        sys.exit(1)

    # Haal een specifieke tekst op
    tekst = db.get_tekst(index_to_get)

    if tekst:
        print(f"\nVoorbeeldtekst voor index {index_to_get} opgehaald:")
        # Print alleen de eerste 40 karakters voor de beknoptheid
        preview = (tekst[:75] + "...") if len(tekst) > 75 else tekst
        print(f"'{preview}'")
    else:
        print(f"\nKon geen tekst vinden voor index {index_to_get}.")

    # Gebruik de nieuwe __len__ methode voor een meer Pythonic aanpak.
    print(f"\nHet totaal aantal items in de database is: {len(db)}")
    print("\n--- Einde van het rapportageprogramma ---")


# Dit is de standaard manier om een Python script uitvoerbaar te maken.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genereert een rapport uit een tekst-database.")
    parser.add_argument("bestandsnaam", help="Het databasebestand om te lezen.")
    parser.add_argument(
        "-i",
        "--index",
        type=int,
        default=1,
        help="De index van het item om op te halen (standaard: 1).",
    )
    args = parser.parse_args()

    maak_rapport(args.bestandsnaam, args.index)
