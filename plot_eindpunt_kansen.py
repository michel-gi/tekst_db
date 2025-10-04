#!/usr/bin/env python3
"""
Een script om de kans op de minimale (of maximale) som te plotten
als functie van het aantal dobbelstenen, om de exponentiële afname te tonen.
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np

from dobbel_utils import bereken_kans_uiterste_worp


def main():
    """Hoofdfunctie van het script."""
    parser = argparse.ArgumentParser(
        description=(
            "Plot de kans op de uiterste worp (allemaal 1'en of allemaal max) als functie van het aantal dobbelstenen."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--max-stenen", type=int, default=10, help="Het maximale aantal dobbelstenen om te plotten.")
    parser.add_argument("-z", "--zijden", type=int, default=6, help="Het aantal zijden van elke dobbelsteen.")
    args = parser.parse_args()

    aantallen_stenen = np.arange(1, args.max_stenen + 1)
    kansen = [bereken_kans_uiterste_worp(n, args.zijden) for n in aantallen_stenen]

    # Maak de plot met twee subplots: een met een lineaire y-as en een met een logaritmische y-as.
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
    fig.suptitle(f"Kans op de uiterste worp voor een d{args.zijden}-dobbelsteen", fontsize=16)

    # --- Plot 1: Lineaire schaal ---
    ax1.plot(aantallen_stenen, kansen, marker="o", linestyle="-", color="blue")
    ax1.set_title("Lineaire Y-as (Laat de snelle afname zien)")
    ax1.set_xlabel("Aantal dobbelstenen")
    ax1.set_ylabel("Kans")
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.set_xticks(aantallen_stenen)

    # --- Plot 2: Logaritmische schaal ---
    ax2.semilogy(aantallen_stenen, kansen, marker="o", linestyle="-", color="green")
    ax2.set_title("Logaritmische Y-as (Bewijst de exponentiële relatie)")
    ax2.set_xlabel("Aantal dobbelstenen")
    ax2.set_ylabel("Kans (log-schaal)")
    ax2.grid(True, which="both", linestyle="--", alpha=0.6)  # Grid voor major en minor ticks
    ax2.set_xticks(aantallen_stenen)

    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Zorg dat de suptitle niet overlapt
    print("Grafiek wordt gegenereerd...")
    plt.show()


if __name__ == "__main__":
    main()
