#!/usr/bin/env python3
# Importeer de class uit de nieuwe module
import argparse
import os
import sys

from database import TextDatabase


def toon_menu():
    """Toont het hoofdmenu met beschikbare opties."""
    print("\nVoer een itemnummer in om de bijbehorende tekst te zien.")
    print("Of kies een van de volgende menu opties:\n")
    print("[n]ieuw   - invoeren van een nieuw tekst item")
    print("[w]ijzig  - wijzigen van een bestaand tekst item")
    print("[v]erwijder - verwijderen van een tekst item")
    print("[o]pslaan  - sla de wijzigingen op")
    print("[p]laats   - verplaats een item naar een nieuwe positie")
    print("[s]top   - beëindig dit programma")
    print("[m]enu   - dit menu opnieuw weergeven")


def main():
    """Hoofdfunctie voor de gebruikersinteractie."""
    parser = argparse.ArgumentParser(
        prog="tekstdb_bewerk",  # Toon de juiste naam in helpberichten
        description="Een interactieve command-line tool om tekst-databases te bewerken.",
        # Zorgt voor correcte weergave van newlines in de helptekst
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "bestandsnaam",
        nargs="?",  # Maakt het argument optioneel
        default="mijn_tekstdatabase.txt",
        help="Het databasebestand om te openen (standaard: mijn_tekstdatabase.txt).",
    )
    parser.add_argument(
        "-c",
        "--create",
        action="store_true",  # Gebruik een flag om aan te geven of een nieuw bestand moet worden aangemaakt
        help="Creëer een nieuw, leeg databasebestand. Overschrijft een bestaand bestand na bevestiging.",
    )

    args = parser.parse_args()

    bestandsnaam = args.bestandsnaam
    create_new = args.create

    if create_new:
        if os.path.exists(bestandsnaam):
            print(f"Waarschuwing: Bestand '{bestandsnaam}' bestaat al.")
            while True:
                bevestiging = input("Weet u zeker dat u dit wilt overschrijven met een lege database? (j/n): ").lower()
                if bevestiging.startswith("j"):
                    break  # Ga door met overschrijven
                elif bevestiging.startswith("n"):
                    print("Operatie geannuleerd.")
                    sys.exit(0)

    # Maak één database object aan. Alle operaties gaan via dit object.
    db = TextDatabase(bestandsnaam, create_new=create_new)
    toon_menu()  # Toon het menu direct bij de start

    while True:
        try:
            aantal_items = len(db.data)
            if aantal_items > 0:
                prompt_tekst = f"\nKies een optie of een nummer (1-{aantal_items}): "
            else:
                # Een meer behulpzame prompt als de database leeg is.
                prompt_tekst = "\nDatabase is leeg. Kies '[n]ieuw' om een item toe te voegen: "

            gebruikers_invoer = input(prompt_tekst)
            invoer_lower = gebruikers_invoer.lower()

            try:
                index_nummer = int(gebruikers_invoer)
                tekst = db.get_tekst(index_nummer)

                if tekst is not None:
                    print(f"\n--- Tekst voor index {index_nummer} ---")
                    print(tekst)
                    print(f"--- Einde tekst voor index {index_nummer} ---")
                else:
                    print(f"Geen tekst gevonden voor index {index_nummer}.")

            except ValueError:  # Not a valid number, check for commands
                match invoer_lower:
                    case "stop" | "s":
                        if db.dirty:
                            while True:
                                bevestiging = input(
                                    "Er zijn niet-opgeslagen wijzigingen. Opslaan voor het stoppen? (j/n): "
                                ).lower()
                                if bevestiging.startswith("j"):
                                    if not db.save():
                                        print("Fout: Kon de database niet opslaan.")
                                        continue  # Blijf in de while-lus, vraag opnieuw
                                    print("Wijzigingen opgeslagen.")
                                    break
                                elif bevestiging.startswith("n"):
                                    break
                        break

                    case "menu" | "m":
                        toon_menu()

                    case "nieuw" | "n":
                        print("Voer de nieuwe tekst in. Laat een lege regel achter om op te slaan.")
                        nieuwe_tekst_regels = []
                        while True:
                            regel = input()
                            if not regel.strip():
                                break
                            nieuwe_tekst_regels.append(regel)

                        nieuwe_tekst = "\n".join(nieuwe_tekst_regels)
                        if db.voeg_tekst_toe(nieuwe_tekst):
                            print("Tekst succesvol toegevoegd (nog niet opgeslagen).")
                            print(f"Totaal aantal items in de database nu: {len(db.data)}")
                        else:
                            print("Fout: Kon de nieuwe tekst niet opslaan.")

                    case "wijzig" | "w":
                        try:
                            index_nummer = int(input("Voer het indexnummer in van de tekst die u wilt wijzigen: "))
                            if index_nummer not in db.data:
                                print(f"Fout: Geen tekst gevonden voor index {index_nummer}.")
                            else:
                                huidige_tekst = db.get_tekst(index_nummer)
                                print(f"\n--- Huidige tekst voor index {index_nummer} ---")
                                print(huidige_tekst)
                                print("--- Einde huidige tekst ---\n")
                                print("\nVoer nu de nieuwe tekst in. Laat een lege regel achter om op te slaan.")
                                nieuwe_tekst_regels = []
                                while True:
                                    regel = input()
                                    if not regel.strip():
                                        break
                                    nieuwe_tekst_regels.append(regel)
                                nieuwe_tekst = "\n".join(nieuwe_tekst_regels)
                                if db.wijzig_tekst(index_nummer, nieuwe_tekst):
                                    bericht = (
                                        f"Tekst voor index {index_nummer} succesvol gewijzigd (nog niet opgeslagen)."
                                    )
                                    print(bericht)
                                else:
                                    print(f"Fout: Kon tekst voor index {index_nummer} niet wijzigen.")
                        except ValueError:
                            print("Ongeldige invoer voor indexnummer. Voer een getal in.")

                    case "verwijder" | "v":
                        try:
                            index_nummer = int(input("Voer het indexnummer in van de tekst die u wilt verwijderen: "))
                            if index_nummer not in db.data:
                                print(f"Fout: Geen tekst gevonden voor index {index_nummer}.")
                            else:
                                verwijder_bericht = (
                                    f"\n--- Tekst voor index {index_nummer} die verwijderd wordt ---\n"
                                    f"{db.get_tekst(index_nummer)}\n--- Einde tekst ---\n"
                                )
                                print(verwijder_bericht)
                                while True:
                                    bevestiging = input(
                                        f"Weet u zeker dat u item {index_nummer} wilt verwijderen? (j/n): "
                                    )
                                    if bevestiging.lower().startswith("j"):
                                        if db.verwijder_tekst(index_nummer):
                                            print(f"Item {index_nummer} succesvol verwijderd (nog niet opgeslagen).")
                                            print(f"Totaal aantal items in de database nu: {len(db.data)}")
                                        else:
                                            print(f"Fout: Kon item {index_nummer} niet verwijderen.")
                                        break
                                    elif bevestiging.lower().startswith("n"):
                                        print(f"Verwijdering van item {index_nummer} geannuleerd.")
                                        break
                                    else:
                                        print("Ongeldige invoer. Voer 'j' of 'n' in.")
                        except ValueError:
                            print("Ongeldige invoer voor indexnummer. Voer een getal in.")
                    case "opslaan" | "o":
                        if db.save():
                            print("Database succesvol opgeslagen.")
                        else:
                            print("Fout: Kon de database niet opslaan.")

                    case "plaats" | "p":
                        try:
                            source_index = int(input("Voer het indexnummer in van het item om te verplaatsen: "))
                            if source_index not in db.data:
                                print(f"Fout: Bronindex {source_index} niet gevonden.")
                            else:
                                dest_index = int(
                                    input(f"Voer de nieuwe positie in voor item {source_index} (1-{len(db.data)}): ")
                                )
                                if db.move_item(source_index, dest_index):
                                    bericht = (
                                        f"Item {source_index} succesvol verplaatst naar "
                                        f"positie {dest_index} (nog niet opgeslagen)."
                                    )
                                    print(bericht)
                                else:
                                    print("Fout: Kon het item niet verplaatsen. Controleer of de doelindex geldig is.")
                        except ValueError:
                            print("Ongeldige invoer voor indexnummer. Voer een getal in.")
                    case _:  # Handle other invalid input (including non-integer which falls through from Try)
                        print(f"Ongeldige invoer. '{gebruikers_invoer}' is geen geldig nummer of commando.")  # type: ignore[possibly-unbound]

        except ValueError:
            print(f"Ongeldige invoer. '{gebruikers_invoer}' is geen geldig nummer of commando.")  # type: ignore[possibly-unbound]


if __name__ == "__main__":
    main()
