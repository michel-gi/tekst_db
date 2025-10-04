#!/usr/bin/env python3
# Zorg ervoor dat dit bestand in dezelfde map staat als tekstlezer.py

# We importeren alleen de TextDatabase class uit de 'database' module.
from database import TextDatabase


def maak_rapport():
    """
    Een voorbeeldprogramma dat de TextDatabase class gebruikt om een rapport te maken.
    """
    print("--- Start van het rapportageprogramma ---")

    # Maak een object van de TextDatabase class.
    # De __init__ methode van de class wordt hier aangeroepen en het bestand wordt geladen.
    db = TextDatabase("mijn_tekstdatabase.txt")

    # Haal een specifieke tekst op
    index_to_get = 2
    tekst = db.get_tekst(index_to_get)

    if tekst:
        print(f"\nVoorbeeldtekst voor index {index_to_get} opgehaald:")
        # Print alleen de eerste 40 karakters voor de beknoptheid
        print(f"'{tekst[:40]}...'")
    else:
        print(f"\nKon geen tekst vinden voor index {index_to_get}.")

    print(f"\nHet totaal aantal items in de database is: {len(db.data)}")
    print("\n--- Einde van het rapportageprogramma ---")


# Dit is de standaard manier om een Python script uitvoerbaar te maken.
if __name__ == "__main__":
    maak_rapport()
