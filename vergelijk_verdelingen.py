#!/usr/bin/env python3
"""
Een Python-script om de theoretische kansverdelingen voor verschillende
aantallen dobbelstenen te berekenen en te vergelijken in één grafiek.
"""

import argparse
import sys

import matplotlib.pyplot as plt

from dobbel_utils import bereken_theoretische_verdeling


def main():
    """Hoofdfunctie van het script."""
    parser = argparse.ArgumentParser(
        description="Vergelijkt de theoretische kansverdelingen van dobbelsteenworpen.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--min-stenen", type=int, default=1, help="Het startaantal dobbelstenen om te plotten.")
    parser.add_argument("--max-stenen", type=int, default=4, help="Het maximale aantal dobbelstenen om te plotten.")
    parser.add_argument("-z", "--zijden", type=int, default=6, help="Het aantal zijden van elke dobbelsteen.")
    args = parser.parse_args()

    if args.min_stenen > args.max_stenen:
        print("Fout: --min-stenen kan niet groter zijn dan --max-stenen.")  # noqa: T201
        sys.exit(1)

    # Maak de plot aan
    fig, ax = plt.subplots(figsize=(12, 8))

    # Loop door de reeks van dobbelstenen
    for aantal_stenen in range(args.min_stenen, args.max_stenen + 1):
        # 1. Bereken de theoretische verdeling
        verdeling = bereken_theoretische_verdeling(aantal_stenen, args.zijden)

        sommen = list(verdeling.keys())
        combinaties = list(verdeling.values())

        # 2. Normaliseer de y-as naar kansen (belangrijk voor vergelijking!).
        totaal_combinaties = sum(combinaties)  # Gelijk aan zijden**aantal_stenen
        kansen = [c / totaal_combinaties for c in combinaties]

        # 3. Centreer de x-as door het gemiddelde af te trekken
        gemiddelde = aantal_stenen * (args.zijden + 1) / 2
        gecentreerde_sommen = [s - gemiddelde for s in sommen]

        # 4. Plot de gecentreerde curve
        ax.plot(gecentreerde_sommen, kansen, marker=".", linestyle="-", label=f"{aantal_stenen} d{args.zijden}")

    # Voeg titels en labels toe
    ax.set_title(f"Gecentreerde Kansverdelingen voor d{args.zijden}-dobbelstenen")
    ax.set_xlabel("Afwijking van het gemiddelde")
    ax.set_ylabel("Kans")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend()  # Toon de legenda

    # Zorg dat de y-as bij 0 begint
    ax.set_ylim(bottom=0)

    print("Grafiek wordt gegenereerd...")  # noqa: T201
    plt.show()


if __name__ == "__main__":
    main()
