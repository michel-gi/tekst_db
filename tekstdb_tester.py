#!/usr/bin/env python3
"""
Een geautomatiseerde test-suite voor de TextDatabase class.

Dit script gebruikt de 'unittest' module van Python om de functionaliteit
van de TextDatabase class te verifiëren. Het kan direct worden uitgevoerd
vanuit de command-line en is bedoeld voor integratie in een CI/CD-workflow.
"""

import os
import unittest

from database import TextDatabase


class TestTextDatabase(unittest.TestCase):
    """
    Test suite voor de TextDatabase class.

    Deze tests zorgen ervoor dat alle database-operaties (aanmaken, lezen,
    wijzigen, verwijderen) correct functioneren.
    """

    test_db_file = "_test_database.txt"

    def setUp(self):
        """
        Wordt voor elke test uitgevoerd. Zorgt voor een schone staat door
        een eventueel oud testdatabase-bestand te verwijderen.
        """
        if os.path.exists(self.test_db_file):
            os.remove(self.test_db_file)

    def tearDown(self):
        """
        Wordt na elke test uitgevoerd. Ruimt op door het testdatabase-bestand
        te verwijderen.
        """
        if os.path.exists(self.test_db_file):
            os.remove(self.test_db_file)

    def test_initialization_and_creation(self):
        """Test het aanmaken van een nieuwe, lege database."""
        db = TextDatabase(self.test_db_file, create_new=True)
        self.assertEqual(len(db), 0)
        self.assertFalse(os.path.exists(self.test_db_file), "Bestand mag niet worden aangemaakt bij initialisatie")

    def test_add_and_save_entry(self):
        """Test het toevoegen van een item en het schrijven naar het bestand."""
        db = TextDatabase(self.test_db_file, create_new=True)
        tekst1 = "Dit is de eerste testtekst."
        db.voeg_tekst_toe(tekst1)

        self.assertTrue(db.save(), "Opslaan naar bestand moet succesvol zijn")
        self.assertEqual(len(db), 1)
        self.assertEqual(db.get_tekst(1), tekst1)
        self.assertTrue(os.path.exists(self.test_db_file), "Bestand moet bestaan na opslaan")

    def test_read_from_existing_file(self):
        """Test of data correct wordt geladen uit een bestaand bestand."""
        # Maak eerst een bestand aan om te lezen
        db1 = TextDatabase(self.test_db_file, create_new=True)
        db1.voeg_tekst_toe("Data om te bewaren")
        db1.save()

        # Maak een nieuwe instance die het bestand leest
        db2 = TextDatabase(self.test_db_file, create_new=False)
        self.assertEqual(len(db2), 1)
        self.assertEqual(db2.get_tekst(1), "Data om te bewaren")
        self.assertIsNone(db2.get_tekst(99), "get_tekst voor niet-bestaande index moet None zijn")

    def test_modify_entry(self):
        """Test het wijzigen van een bestaand item."""
        db = TextDatabase(self.test_db_file, create_new=True)
        db.voeg_tekst_toe("Originele tekst")
        nieuwe_tekst = "Gewijzigde tekst"

        self.assertTrue(db.wijzig_tekst(1, nieuwe_tekst), "Wijzigen moet succesvol zijn")
        self.assertEqual(db.get_tekst(1), nieuwe_tekst)
        self.assertFalse(db.wijzig_tekst(99, "Zal niet werken"), "Moet falen voor niet-bestaande index")

    def test_delete_and_reindex(self):
        """Test het verwijderen van een item en de daaropvolgende herindexering."""
        db = TextDatabase(self.test_db_file, create_new=True)
        db.voeg_tekst_toe("Item 1")
        db.voeg_tekst_toe("Item 2")
        db.voeg_tekst_toe("Item 3")

        self.assertTrue(db.verwijder_tekst(2), "Verwijderen moet succesvol zijn")
        self.assertEqual(len(db), 2, "Er moeten 2 items overblijven")
        self.assertEqual(db.get_tekst(1), "Item 1")
        self.assertEqual(db.get_tekst(2), "Item 3", "Item 3 moet nu index 2 hebben")
        self.assertIsNone(db.get_tekst(3), "Oude index 3 moet leeg zijn")
        self.assertEqual(list(db.data.keys()), [1, 2])
        self.assertFalse(db.verwijder_tekst(99), "Moet falen voor niet-bestaande index")

    def test_add_at_index(self):
        """Test het toevoegen van een item op een specifieke index."""
        db = TextDatabase(self.test_db_file, create_new=True)
        db.voeg_tekst_toe("Item A")
        db.voeg_tekst_toe("Item C")

        # Voeg "Item B" in op index 2
        self.assertTrue(db.voeg_tekst_op_index_toe(2, "Item B"))
        self.assertEqual(len(db), 3)
        self.assertEqual(db.get_tekst(1), "Item A")
        self.assertEqual(db.get_tekst(2), "Item B")
        self.assertEqual(db.get_tekst(3), "Item C")

        # Voeg "Item D" toe aan het einde
        self.assertTrue(db.voeg_tekst_op_index_toe(4, "Item D"))
        self.assertEqual(db.get_tekst(4), "Item D")

        # Voeg "Item 0" toe aan het begin
        self.assertTrue(db.voeg_tekst_op_index_toe(1, "Item 0"))
        self.assertEqual(db.get_tekst(1), "Item 0")
        self.assertEqual(db.get_tekst(2), "Item A")
        self.assertEqual(len(db), 5)

        # Test met ongeldige indexen en vang de verwachte waarschuwingen op
        with self.assertLogs(level="WARNING") as cm:
            self.assertFalse(db.voeg_tekst_op_index_toe(0, "Zal falen"), "Toevoegen op index 0 moet falen")
            self.assertIn("Doelindex 0 is buiten bereik", cm.records[0].getMessage())

        with self.assertLogs(level="WARNING") as cm:
            self.assertFalse(db.voeg_tekst_op_index_toe(7, "Zal ook falen"), "Toevoegen buiten bereik moet falen")
            self.assertIn("Doelindex 7 is buiten bereik", cm.records[0].getMessage())

    def test_move_item(self):
        """Test het verplaatsen van een item en de daaropvolgende herindexering."""
        db = TextDatabase(self.test_db_file, create_new=True)
        db.voeg_tekst_toe("Item 1")
        db.voeg_tekst_toe("Item 2")
        db.voeg_tekst_toe("Item 3")
        db.voeg_tekst_toe("Item 4")

        # Test 1: Verplaats item 2 naar positie 4
        self.assertTrue(db.move_item(2, 4))
        self.assertEqual(db.get_tekst(1), "Item 1")
        self.assertEqual(db.get_tekst(2), "Item 3")
        self.assertEqual(db.get_tekst(3), "Item 4")
        self.assertEqual(db.get_tekst(4), "Item 2")

        # Test 2: Verplaats item 1 (nu "Item 1") naar positie 3
        self.assertTrue(db.move_item(1, 3))
        self.assertEqual(db.get_tekst(1), "Item 3")
        self.assertEqual(db.get_tekst(2), "Item 4")
        self.assertEqual(db.get_tekst(3), "Item 1")
        self.assertEqual(db.get_tekst(4), "Item 2")

        # Test 3: Ongeldige indexen
        with self.assertLogs(level="WARNING") as cm:
            self.assertFalse(db.move_item(99, 1), "Verplaatsen met niet-bestaande bronindex moet falen")
            self.assertIn("Bronindex 99 niet gevonden", cm.records[0].getMessage())

        with self.assertLogs(level="WARNING") as cm:
            self.assertFalse(db.move_item(1, 99), "Verplaatsen naar niet-bestaande doelindex moet falen")
            self.assertIn("Doelindex 99 is buiten bereik", cm.records[0].getMessage())

    def test_reindex_on_load(self):
        """Test of de database zichzelf herindexeert bij het laden van een 'rommelig' bestand."""
        # Maak handmatig een bestand met niet-opeenvolgende indices
        malformed_content = (
            "###INDEX: 5\nTekst voor index 5\n\n"
            "###INDEX: 2\nTekst voor index 2\n\n"
            "###INDEX: 10\nTekst voor index 10\n\n"
        )
        with open(self.test_db_file, "w", encoding="utf-8") as f:
            f.write(malformed_content)

        # Laad de database. De _reindex_if_needed methode zou moeten draaien.
        db = TextDatabase(self.test_db_file)

        # Controleer of de indices nu netjes 1, 2, 3 zijn
        self.assertEqual(list(db.data.keys()), [1, 2, 3])
        # Controleer of de data bewaard is gebleven in de juiste volgorde (gesorteerd op oude index)
        self.assertEqual(db.get_tekst(1), "Tekst voor index 2")
        self.assertEqual(db.get_tekst(2), "Tekst voor index 5")
        self.assertEqual(db.get_tekst(3), "Tekst voor index 10")
        # Controleer of de 'dirty' flag is gezet, omdat er een wijziging (herindexering) heeft plaatsgevonden
        self.assertTrue(db.dirty, "Dirty flag moet True zijn na herindexering")


if __name__ == "__main__":
    # Dit maakt het script uitvoerbaar en start de test runner.
    # De test runner vindt automatisch alle methodes die met 'test_' beginnen.
    unittest.main(verbosity=2)
