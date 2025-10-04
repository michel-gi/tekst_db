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


def _vraag_index(prompt_tekst, max_index):
    """Vraagt de gebruiker om een index en valideert deze."""
    try:
        index = int(input(prompt_tekst))
        if 1 <= index <= max_index:
            return index
        print(f"Fout: Index moet tussen 1 en {max_index} liggen.")
        return None
    except ValueError:
        print("Ongeldige invoer. Voer een getal in.")
        return None


def _vraag_multiline_tekst(prompt):
    """Vraagt de gebruiker om meerdere regels tekst."""
    print(prompt)
    regels = []
    while True:
        try:
            regel = input()
            if not regel.strip():
                break
            regels.append(regel)
        except EOFError:  # Ctrl+D
            break
    return "\n".join(regels)


def _vraag_bevestiging(prompt):
    """Vraagt om een 'j/n' bevestiging en geeft een boolean terug."""
    while True:
        antwoord = input(prompt).lower()
        if antwoord.startswith("j"):
            return True
        if antwoord.startswith("n"):
            return False
        print("Ongeldige invoer. Voer 'j' of 'n' in.")


def _handel_nieuw(db):
    """Handelt het toevoegen van een nieuw item af."""
    nieuwe_tekst = _vraag_multiline_tekst("Voer de nieuwe tekst in. Sluit af met een lege regel.")
    if nieuwe_tekst and db.voeg_tekst_toe(nieuwe_tekst):
        print("Tekst succesvol toegevoegd (nog niet opgeslagen).")
        print(f"Totaal aantal items in de database nu: {len(db)}")
    elif nieuwe_tekst:
        print("Fout: Kon de nieuwe tekst niet toevoegen.")


def _handel_wijzig(db):
    """Handelt het wijzigen van een bestaand item af."""
    index = _vraag_index(f"Index om te wijzigen (1-{len(db)}): ", len(db))
    if index is None:
        return

    huidige_tekst = db.get_tekst(index)
    print(f"\n--- Huidige tekst voor index {index} ---\n{huidige_tekst}\n--- Einde huidige tekst ---")
    nieuwe_tekst = _vraag_multiline_tekst("\nVoer de nieuwe tekst in. Sluit af met een lege regel.")

    if nieuwe_tekst and db.wijzig_tekst(index, nieuwe_tekst):
        print(f"Tekst voor index {index} succesvol gewijzigd (nog niet opgeslagen).")
    elif nieuwe_tekst:
        print(f"Fout: Kon tekst voor index {index} niet wijzigen.")


def _handel_verwijder(db):
    """Handelt het verwijderen van een item af."""
    index = _vraag_index(f"Index om te verwijderen (1-{len(db)}): ", len(db))
    if index is None:
        return

    print(f"\n--- Tekst voor index {index} ---\n{db.get_tekst(index)}\n--- Einde tekst ---")
    if _vraag_bevestiging(f"Weet u zeker dat u item {index} wilt verwijderen? (j/n): "):
        if db.verwijder_tekst(index):
            print(f"Item {index} succesvol verwijderd (nog niet opgeslagen).")
            print(f"Totaal aantal items in de database nu: {len(db)}")
        else:
            print(f"Fout: Kon item {index} niet verwijderen.")
    else:
        print(f"Verwijdering van item {index} geannuleerd.")


def _handel_plaats(db):
    """Handelt het verplaatsen van een item af."""
    source_index = _vraag_index(f"Item om te verplaatsen (1-{len(db)}): ", len(db))
    if source_index is None:
        return

    dest_index = _vraag_index(f"Nieuwe positie voor item {source_index} (1-{len(db)}): ", len(db))
    if dest_index is None:
        return

    if db.move_item(source_index, dest_index):
        print(f"Item {source_index} succesvol verplaatst naar positie {dest_index} (nog niet opgeslagen).")
    else:
        print("Fout: Kon het item niet verplaatsen.")


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
            prompt = "Weet u zeker dat u dit wilt overschrijven met een lege database? (j/n): "
            if not _vraag_bevestiging(prompt):
                print("Operatie geannuleerd.")
                sys.exit(0)

    # Maak één database object aan. Alle operaties gaan via dit object.
    db = TextDatabase(bestandsnaam, create_new=create_new)
    toon_menu()  # Toon het menu direct bij de start

    while True:
        try:
            aantal_items = len(db)
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
                            prompt = "Er zijn niet-opgeslagen wijzigingen. Opslaan voor het stoppen? (j/n): "
                            if _vraag_bevestiging(prompt):
                                if db.save():
                                    print("Wijzigingen opgeslagen.")
                                else:
                                    print("Fout: Kon de database niet opslaan.")
                                    continue  # Blijf in de lus
                        break

                    case "menu" | "m":
                        toon_menu()

                    case "nieuw" | "n":
                        _handel_nieuw(db)

                    case "wijzig" | "w":
                        _handel_wijzig(db)

                    case "verwijder" | "v":
                        _handel_verwijder(db)

                    case "opslaan" | "o":
                        if db.save():
                            print("Database succesvol opgeslagen.")
                        else:
                            print("Fout: Kon de database niet opslaan.")

                    case "plaats" | "p":
                        _handel_plaats(db)

                    case _:  # Handle other invalid input (including non-integer which falls through from Try)
                        print(f"Ongeldige invoer. '{gebruikers_invoer}' is geen geldig nummer of commando.")  # type: ignore[possibly-unbound]

        except ValueError:
            print(f"Ongeldige invoer. '{gebruikers_invoer}' is geen geldig nummer of commando.")  # type: ignore[possibly-unbound]


if __name__ == "__main__":
    main()
