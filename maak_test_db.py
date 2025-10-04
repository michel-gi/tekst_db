#!/usr/bin/env python3
"""
Een hulpprogramma om een testdatabase te genereren.

Dit script maakt een bestand aan (standaard 'mijn_tekstdatabase.txt')
en vult het met een aantal voorbeeld-tekstitems.
Bestaande bestanden worden zonder waarschuwing overschreven.
"""

import argparse
import sys

from database import TextDatabase

# Voorbeelddata voor de testdatabase
VOORBEELD_DATA = [
    "Dit is het eerste item in de database.\nHet kan meerdere regels bevatten.",
    "Het tweede item is een kort stukje tekst.",
    "Derde item.\n\nMet een extra witregel in het midden.",
    "En hier is een vierde, wat langer item om de lijst wat meer body te geven. "
    "Dit is nuttig voor het testen van de weergave in de GUI en de zoekfunctionaliteit.",
    "Het vijfde en laatste voorbeelditem.",
]


def maak_test_database(bestandsnaam, data):
    """
    Maakt een nieuwe database aan en vult deze met de opgegeven data.

    Args:
        bestandsnaam (str): De naam van het te creëren databasebestand.
        data (list[str]): Een lijst met strings om als items toe te voegen.
    """
    print(f"Bezig met het aanmaken van testdatabase '{bestandsnaam}'...")

    try:
        # Gebruik create_new=True om een eventueel bestaand bestand te overschrijven
        db = TextDatabase(bestandsnaam, create_new=True)

        for tekst in data:
            db.voeg_tekst_toe(tekst)

        if db.save():
            print(f"Succes! Testdatabase '{bestandsnaam}' aangemaakt met {len(db)} items.")
        else:
            print(f"Fout: Kon de database niet opslaan naar '{bestandsnaam}'.", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Een onverwachte fout is opgetreden: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genereert een test-databasebestand.")
    parser.add_argument("bestandsnaam", nargs="?", default="mijn_tekstdatabase.txt", help="De naam van het te creëren databasebestand (standaard: mijn_tekstdatabase.txt).")
    args = parser.parse_args()

    maak_test_database(args.bestandsnaam, VOORBEELD_DATA)