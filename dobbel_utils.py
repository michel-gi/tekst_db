# /home/michel/projects/dobbelen/dobbel_utils.py
import numpy as np


def bereken_theoretische_verdeling(aantal_dobbelstenen: int, aantal_zijden: int) -> dict[int, int]:
    """
    Berekent de exacte kansverdeling met behulp van convolutie.
    Geeft het aantal combinaties voor elke mogelijke som terug.
    Deze versie gebruikt NumPy voor efficiëntie.
    """
    # We gebruiken dtype=object om NumPy te dwingen Python's arbitrary-precision
    # integers te gebruiken. Dit voorkomt integer overflow.
    basis_verdeling = np.array([1] * aantal_zijden, dtype=object)
    huidige_verdeling = basis_verdeling

    for _ in range(1, aantal_dobbelstenen):
        huidige_verdeling = np.convolve(huidige_verdeling, basis_verdeling)

    min_som = aantal_dobbelstenen
    return {i + min_som: combinaties for i, combinaties in enumerate(huidige_verdeling)}


def bereken_kans_uiterste_worp(aantal_stenen: int, aantal_zijden: int) -> float:
    """
    Berekent de kans op de uiterste worp (allemaal 1'en of allemaal max).
    """
    return 1 / (aantal_zijden**aantal_stenen)
