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

    def test_01_initialization_and_creation(self):
        """Test het aanmaken van een nieuwe, lege database."""
        db = TextDatabase(self.test_db_file, create_new=True)
        self.assertEqual(db.data, {})
        self.assertFalse(os.path.exists(self.test_db_file), "Bestand mag niet worden aangemaakt bij initialisatie")

    def test_02_add_and_write_entry(self):
        """Test het toevoegen van een item en het schrijven naar het bestand."""
        db = TextDatabase(self.test_db_file, create_new=True)
        tekst1 = "Dit is de eerste testtekst."
        db.voeg_tekst_toe(tekst1)  # Werkt nu alleen in-memory

        # Expliciet opslaan en het resultaat daarvan controleren
        result = db.save()
        self.assertTrue(result, "Opslaan naar bestand moet succesvol zijn")
        self.assertEqual(len(db.data), 1)
        self.assertEqual(db.get_tekst(1), tekst1)
        self.assertTrue(os.path.exists(self.test_db_file), "Bestand moet bestaan na opslaan")

    def test_03_read_from_existing_file(self):
        """Test of data correct wordt geladen uit een bestaand bestand."""
        db1 = TextDatabase(self.test_db_file, create_new=True)
        db1.voeg_tekst_toe("Data om te bewaren")
        db1.save()  # Expliciet opslaan is nu nodig voordat een andere instance kan lezen.
        db2 = TextDatabase(self.test_db_file, create_new=False)
        self.assertEqual(len(db2.data), 1)
        self.assertEqual(db2.get_tekst(1), "Data om te bewaren")
        self.assertIsNone(db2.get_tekst(99), "get_tekst voor niet-bestaande index moet None zijn")

    def test_04_modify_entry(self):
        """Test het wijzigen van een bestaand item."""
        db = TextDatabase(self.test_db_file, create_new=True)
        db.voeg_tekst_toe("Originele tekst")
        nieuwe_tekst = "Gewijzigde tekst"
        result = db.wijzig_tekst(1, nieuwe_tekst)
        self.assertTrue(result, "Wijzigen moet succesvol zijn")
        self.assertEqual(db.get_tekst(1), nieuwe_tekst)
        self.assertFalse(db.wijzig_tekst(99, "Zal niet werken"), "Moet falen voor niet-bestaande index")

    def test_05_delete_and_reindex(self):
        """Test het verwijderen van een item en de daaropvolgende herindexering."""
        db = TextDatabase(self.test_db_file, create_new=True)
        db.voeg_tekst_toe("Item 1")
        db.voeg_tekst_toe("Item 2")
        db.voeg_tekst_toe("Item 3")
        result = db.verwijder_tekst(2)
        self.assertTrue(result, "Verwijderen moet succesvol zijn")
        self.assertEqual(len(db.data), 2, "Er moeten 2 items overblijven")
        self.assertEqual(db.get_tekst(1), "Item 1")
        self.assertEqual(db.get_tekst(2), "Item 3", "Item 3 moet nu index 2 hebben")
        self.assertIsNone(db.get_tekst(3), "Oude index 3 moet leeg zijn")
        self.assertEqual(list(db.data.keys()), [1, 2])
        self.assertFalse(db.verwijder_tekst(99), "Moet falen voor niet-bestaande index")

    def test_06_move_item(self):
        """Test het verplaatsen van een item en de daaropvolgende herindexering."""
        db = TextDatabase(self.test_db_file, create_new=True)
        db.voeg_tekst_toe("Item 1")
        db.voeg_tekst_toe("Item 2")
        db.voeg_tekst_toe("Item 3")
        db.voeg_tekst_toe("Item 4")

        # Verplaats item 2 naar positie 4
        self.assertTrue(db.move_item(2, 4))
        self.assertEqual(db.get_tekst(1), "Item 1")
        self.assertEqual(db.get_tekst(2), "Item 3")
        self.assertEqual(db.get_tekst(3), "Item 4")
        self.assertEqual(db.get_tekst(4), "Item 2")

        # Verplaats item 1 (nu "Item 1") naar positie 3
        self.assertTrue(db.move_item(1, 3))
        self.assertEqual(db.get_tekst(1), "Item 3")
        self.assertEqual(db.get_tekst(2), "Item 4")
        self.assertEqual(db.get_tekst(3), "Item 1")
        self.assertEqual(db.get_tekst(4), "Item 2")

        # Test met ongeldige indexen en vang de verwachte waarschuwingen op
        with self.assertLogs(level="WARNING") as cm:
            self.assertFalse(db.move_item(99, 1), "Verplaatsen met niet-bestaande bronindex moet falen")
            self.assertIn("Bronindex 99 niet gevonden", cm.records[0].getMessage())

        with self.assertLogs(level="WARNING") as cm:
            self.assertFalse(db.move_item(1, 99), "Verplaatsen naar niet-bestaande doelindex moet falen")
            self.assertIn("Doelindex 99 is buiten bereik", cm.records[0].getMessage())

        with self.assertLogs(level="WARNING") as cm:
            self.assertFalse(db.move_item(1, 0), "Verplaatsen naar ongeldige doelindex (0) moet falen")
            self.assertIn("Doelindex 0 is buiten bereik", cm.records[0].getMessage())

    def test_07_add_at_index(self):
        """Test het toevoegen van een item op een specifieke index."""
        db = TextDatabase(self.test_db_file, create_new=True)
        db.voeg_tekst_toe("Item A")
        db.voeg_tekst_toe("Item C")

        # Voeg "Item B" in op index 2
        self.assertTrue(db.voeg_tekst_op_index_toe(2, "Item B"))
        self.assertEqual(len(db.data), 3)
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
        self.assertEqual(len(db.data), 5)

        # Test met ongeldige indexen en vang de verwachte waarschuwingen op
        with self.assertLogs(level="WARNING") as cm:
            self.assertFalse(db.voeg_tekst_op_index_toe(0, "Zal falen"), "Toevoegen op index 0 moet falen")
            self.assertIn("Doelindex 0 is buiten bereik", cm.records[0].getMessage())

        with self.assertLogs(level="WARNING") as cm:
            self.assertFalse(db.voeg_tekst_op_index_toe(7, "Zal ook falen"), "Toevoegen buiten bereik moet falen")
            self.assertIn("Doelindex 7 is buiten bereik", cm.records[0].getMessage())


if __name__ == "__main__":
    # Dit maakt het script uitvoerbaar en start de test runner.
    # De test runner vindt automatisch alle methodes die met 'test_' beginnen.
    unittest.main(verbosity=2)
