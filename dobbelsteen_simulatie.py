#!/usr/bin/env python3
"""
Een Python-script om de kansverdeling van dobbelsteenworpen te simuleren.
"""

import argparse
import sys
import tkinter as tk
from collections import Counter
from tkinter import messagebox, ttk

import numpy as np

from dobbel_utils import bereken_theoretische_verdeling

# Probeer matplotlib te importeren en geef een duidelijke foutmelding als het niet lukt.
try:
    import matplotlib.pyplot as plt
except ImportError:
    # This runs before any GUI is initialized, so print is acceptable here.
    print("Fout: De 'matplotlib' bibliotheek is niet gevonden.")
    print("Installeer deze met het commando: python3 -m pip install matplotlib")
    sys.exit(1)


def simuleer_worpen(aantal_dobbelstenen, aantal_worpen, aantal_zijden):
    """
    Simuleert een serie worpen met een gegeven aantal dobbelstenen.

    Args:
        aantal_dobbelstenen (int): Het aantal dobbelstenen per worp.
        aantal_worpen (int): Het totale aantal worpen dat gesimuleerd wordt.
        aantal_zijden (int): Het aantal zijden van elke dobbelsteen.

    Returns:
        collections.Counter: Een object met de som van de worpen als sleutel
                             en de frequentie als waarde.
    """
    # This print is for direct user feedback in CLI mode, which is a primary function.
    # We can leave it, or use logging if we configure a handler for stdout.
    simulatie_bericht = (
        f"Simulatie gestart: {aantal_worpen:,} worpen met {aantal_dobbelstenen} d{aantal_zijden}-dobbelstenen..."
    )
    print(simulatie_bericht.replace(",", "."))

    # Genereer alle worpen in één keer met NumPy voor hoge prestaties
    worpen = np.random.randint(1, aantal_zijden + 1, size=(aantal_worpen, aantal_dobbelstenen))
    # Tel de som per worp (langs de tweede as)
    sommen = np.sum(worpen, axis=1)
    # Counter telt automatisch hoe vaak elke unieke som voorkomt
    return Counter(sommen)


def toon_verdeling_tekstueel(resultaten, schaal=100):
    """Toont de verdeling als een eenvoudige tekstuele histogram."""
    print("\n--- Tekstuele Verdeling van de Resultaten ---")
    # Sorteer de resultaten op basis van de som (de sleutel)
    if not resultaten:
        print("Geen resultaten om te tonen.")
        return

    gesorteerde_resultaten = sorted(resultaten.items())
    totaal_worpen = sum(resultaten.values())

    # Vind de hoogste frequentie voor het schalen van de balken
    max_frequentie = max(item[1] for item in gesorteerde_resultaten) if gesorteerde_resultaten else 1

    for som, frequentie in gesorteerde_resultaten:
        # Bereken de lengte van de visuele balk
        balk_lengte = int((frequentie / max_frequentie) * schaal) if max_frequentie > 0 else 0
        balk = "#" * balk_lengte
        percentage = (frequentie / totaal_worpen) * 100
        resultaat_bericht = f"Som {som:2d}: {frequentie:7,d} keer ({percentage:5.2f}%) | {balk}"
        print(resultaat_bericht.replace(",", "."))


def toon_verdeling_grafisch(
    simulatie_resultaten,
    aantal_dobbelstenen,
    aantal_worpen,
    aantal_zijden,
    theoretische_verdeling=None,
):
    """
    Toont de verdeling van de resultaten in een staafdiagram met matplotlib.
    Kan ook de theoretische verdeling als een lijn plotten.
    """
    # Sorteer de data op de som (sleutel) voor een logische grafiek
    gesorteerde_items = sorted(simulatie_resultaten.items())
    sommen = [item[0] for item in gesorteerde_items]
    frequenties = [item[1] for item in gesorteerde_items]

    # Maak de plot
    plt.figure(figsize=(12, 7))  # Maak de grafiek wat breder
    plt.bar(sommen, frequenties, color="skyblue", edgecolor="black", label="Simulatie")

    # Voeg titels en labels toe
    titel = f"Verdeling van {aantal_worpen:,} worpen met {aantal_dobbelstenen} d{aantal_zijden}-dobbelstenen"
    plt.title(titel.replace(",", "."))
    plt.xlabel("Som van de ogen")
    plt.ylabel("Frequentie")

    # Plot de theoretische verdeling als die is meegegeven
    if theoretische_verdeling:
        theoretische_sommen = sorted(theoretische_verdeling.keys())
        theoretische_combinaties = [theoretische_verdeling[s] for s in theoretische_sommen]

        # Schaal de theoretische data zodat deze vergelijkbaar is met de simulatie.
        # Het totale aantal combinaties is simpelweg zijden^stenen.
        # Dit is veel sneller en robuuster dan de hele lijst optellen.
        totaal_combinaties = float(aantal_zijden**aantal_dobbelstenen)
        schaal_factor = aantal_worpen / totaal_combinaties if totaal_combinaties > 0 else 0
        geschaalde_frequenties = [c * schaal_factor for c in theoretische_combinaties]

        plt.plot(
            theoretische_sommen,
            geschaalde_frequenties,
            color="red",
            marker="o",
            linestyle="-",
            linewidth=2,
            label="Theorie",
        )

    # Zorg ervoor dat alle integers op de x-as worden getoond
    min_som = aantal_dobbelstenen
    max_som = aantal_dobbelstenen * aantal_zijden
    # Als er veel mogelijke sommen zijn, toon niet elke tick om overlap te voorkomen
    if max_som - min_som < 35:
        plt.xticks(range(min_som, max_som + 1))
    else:
        # Toon bijvoorbeeld elke 5e of 10e tick
        stap_grootte = 5 if max_som - min_som < 100 else 10
        plt.xticks(range(min_som, max_som + 1, stap_grootte))

    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.legend()
    plt.show()


def run_simulatie(aantal_dobbelstenen, aantal_zijden, aantal_worpen):
    """Voert de daadwerkelijke simulatie en plotting uit."""
    # De print-statements hieronder zijn vooral nuttig voor de CLI-modus.
    # In de GUI-modus (met --windowed) zijn ze niet zichtbaar.
    simulatie_resultaten = simuleer_worpen(aantal_dobbelstenen, aantal_worpen, aantal_zijden)
    theoretische_verdeling = bereken_theoretische_verdeling(aantal_dobbelstenen, aantal_zijden)

    toon_verdeling_tekstueel(simulatie_resultaten)
    toon_verdeling_grafisch(
        simulatie_resultaten, aantal_dobbelstenen, aantal_worpen, aantal_zijden, theoretische_verdeling
    )


class DobbelsteenApp:
    """De Tkinter GUI voor de dobbelsteen simulatie."""

    def __init__(self, master):
        self.master = master
        master.title("Dobbelsteen Simulatie")
        master.resizable(False, False)  # Maak het venster niet-schaalbaar

        # Maak de menubalk
        self.create_menu()

        # Gebruik ttk voor modernere widgets
        self.frame = ttk.Frame(master, padding="10")
        self.frame.grid(row=0, column=0, sticky="nsew")

        # Invoervelden en labels
        ttk.Label(self.frame, text="Aantal dobbelstenen:").grid(column=0, row=0, sticky=tk.W, pady=2)
        self.stenen_var = tk.StringVar(value="3")
        ttk.Entry(self.frame, width=10, textvariable=self.stenen_var).grid(column=1, row=0, sticky=tk.E, pady=2)

        ttk.Label(self.frame, text="Aantal zijden per steen:").grid(column=0, row=1, sticky=tk.W, pady=2)
        self.zijden_var = tk.StringVar(value="6")
        ttk.Entry(self.frame, width=10, textvariable=self.zijden_var).grid(column=1, row=1, sticky=tk.E, pady=2)

        ttk.Label(self.frame, text="Aantal worpen:").grid(column=0, row=2, sticky=tk.W, pady=2)
        self.worpen_var = tk.StringVar(value="100000")
        ttk.Entry(self.frame, width=10, textvariable=self.worpen_var).grid(column=1, row=2, sticky=tk.E, pady=2)

        # Knop om de simulatie te starten
        ttk.Button(self.frame, text="Start Simulatie", command=self.start_simulatie_gui).grid(
            column=0, row=3, columnspan=2, pady=10
        )

    def create_menu(self):
        """Maakt de menubalk voor de applicatie."""
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        # Voeg een "Help" menu toe
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Over...", command=self.show_about)

    def show_about(self):
        """Toont het 'Over' dialoogvenster."""
        about_message = (
            "Dobbelsteen Simulatie v1.0\n\n"
            "Een programma om dobbelsteenworpen te simuleren en de kansverdeling te visualiseren.\n\n"
            "Gemaakt met Python, Tkinter en Matplotlib."
        )
        messagebox.showinfo("Over Dobbelsteen Simulatie", about_message)

    def start_simulatie_gui(self):
        """Haalt waarden uit de GUI, valideert ze en start de simulatie."""
        try:
            stenen = int(self.stenen_var.get())
            zijden = int(self.zijden_var.get())
            worpen = int(self.worpen_var.get())

            if not all(x > 0 for x in [stenen, zijden, worpen]):
                messagebox.showerror("Fout", "Alle waarden moeten positieve getallen zijn.")
                return

            # Voeg een extra controle toe voor zeer grote waarden om lange wachttijden te voorkomen
            if stenen > 50:
                waarschuwing_bericht = f"Een simulatie met {stenen} dobbelstenen kan erg lang duren. Wilt u doorgaan?"
                if not messagebox.askokcancel("Waarschuwing", waarschuwing_bericht):
                    return
            if zijden > 1000:
                messagebox.showwarning(
                    "Waarschuwing", f"Een dobbelsteen met {zijden} zijden kan de berekening vertragen."
                )

            # Roep de bestaande logica aan
            run_simulatie(stenen, zijden, worpen)

        except ValueError:
            messagebox.showerror("Fout", "Ongeldige invoer. Zorg ervoor dat alle velden gehele getallen zijn.")


def main():
    """Hoofdfunctie van het script."""
    # Als er command-line argumenten zijn (naast de scriptnaam zelf),
    # draaien we in de command-line modus voor backward compatibility.
    if len(sys.argv) > 1:
        main_cli()
    else:
        # Geen argumenten: start de GUI-modus
        root = tk.Tk()
        # The 'app' instance is not used, but creating it sets up the GUI.
        # The linter flags this as F841, so we avoid assignment.
        DobbelsteenApp(root)
        root.mainloop()


def main_cli():
    """De originele command-line interface logica."""
    parser = argparse.ArgumentParser(
        description="Simuleert dobbelsteenworpen en toont de kansverdeling.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-s", "--stenen", type=int, default=3, help="Het aantal dobbelstenen per worp.")
    parser.add_argument("-z", "--zijden", type=int, default=6, help="Het aantal zijden van elke dobbelsteen.")
    parser.add_argument("-w", "--worpen", type=int, default=100000, help="Het totale aantal worpen.")
    args = parser.parse_args()
    run_simulatie(args.stenen, args.zijden, args.worpen)


if __name__ == "__main__":
    main()
