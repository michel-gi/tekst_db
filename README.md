# Dobbelen Project

A collection of Python tools for simulating dice rolls and analyzing the resulting probability distributions. This project features several graphical and console-based applications built with `tkinter`, `matplotlib`, and `numpy`.

## Features

This project consists of several standalone applications:

### GUI Applications

* **`dobbelsteen_simulatie`**: The main application for running various dice roll simulations and visualizing the outcomes. It includes an icon and version information.
* **`vergelijk_verdelingen`**:  A tool to visually compare different probability distributions generated from simulations.
* **`plot_eindpunt_kansen`**:  An application to plot the probabilities of final outcomes in multi-step simulations.
* **`tekstdb_gui`**: A graphical user interface for managing the text database.

### Console Applications

* **`tekstdb_bewerk`**: A command-line tool for managing the text-based database (`database.py`) used by the applications.
* **`tekstdb_tester`**: A utility to test the integrity and functionality of the text database.

## Core Components

### `database.py` - The Text Database

At the heart of several applications in this project is a simple, custom-built text database managed by the `TextDatabase` class in `database.py`.

* **Purpose**: To provide a lightweight, human-readable way to store and manage indexed blocks of text in a single file.
* **Format**: It uses a simple format where each entry is preceded by a unique `###INDEX: <number>` marker.
* **Functionality**: The class handles all the necessary operations:
  * Reading and parsing the database file.
  * Adding, modifying, and deleting entries.
  * Automatically re-indexing entries when one is removed to maintain a compact index.
* **Usage**: This component is used by the `tekstdb_bewerk` and `tekstdb_tester` console applications to manage and verify the data.

### `dobbel_utils.py` - Calculation Utilities

This module contains shared mathematical functions used by multiple applications in the project to avoid code duplication.

* **`bereken_theoretische_verdeling`**: Calculates the exact probability distribution for a given number of dice using convolution. This is used by `dobbelsteen_simulatie.py` and `vergelijk_verdelingen.py` to compare simulated results against theoretical probabilities.
* **`bereken_kans_uiterste_worp`**: A simple function to calculate the probability of an extreme outcome (e.g., all ones or all sixes). This is used by `plot_eindpunt_kansen.py` to demonstrate the exponential decrease in probability as more dice are added.

## Getting Started

The easiest way to use these tools is to download the pre-built executables for your operating system from the project's GitHub Releases page.

1. Go to the [**Releases**](https://github.com/[your-github-username]/[your-repo-name]/releases) page of this repository.
2. Find the latest release.
3. Under the **Assets** section, download the file corresponding to your operating system (Windows, macOS, or Linux) and the script you want to use.

### Running the Applications

* **Windows**: Download the `.exe` file and double-click it to run.
* **macOS / Linux**: Download the executable file. You may need to make it executable before running it from your terminal:

    ```bash

    # Example for the main simulation on Linux
    chmod +x ./dobbelsteen_simulatie-linux
    ./dobbelsteen_simulatie-linux
    ```

## Building from Source

If you prefer to build the applications yourself, you can do so by following these steps.

### Prerequisites

* Python 3.12
* Git

### Steps

1. **Clone the repository:**

    ```bash
    git clone https://github.com/[your-github-username]/[your-repo-name].git
    cd dobbelen
    ```

2. **Set up a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up pre-commit hooks (for development):**
   This project uses `pre-commit` to ensure code quality. After installing the dependencies, run the following command to set up the Git hooks:

    ```bash
    pre-commit install
    ```

   This will run checks automatically every time you make a new commit.

5. **Build with PyInstaller:**
    The project uses PyInstaller to create the executables. The build process is defined in the GitHub Actions workflow at `.github/workflows/build.yml`.

    To build a specific script, you can run one of the following commands:

    ```bash
    # For a GUI application like dobbelsteen_simulatie
    pyinstaller --onefile --windowed --hidden-import PIL._tkinter_finder dobbelsteen_simulatie.py

    # For a console application like tekstdb_bewerk
    pyinstaller --onefile --console tekstdb_bewerk.py
    ```

    The resulting executable will be located in the `dist/` directory.

## Continuous Integration

This project uses GitHub Actions for Continuous Integration and Continuous Deployment (CI/CD). On every push to the `main` branch, the following automated process is triggered:

1. Jobs are initiated for Windows, macOS, and Linux environments.
2. All Python dependencies from `requirements.txt` are installed.
3. PyInstaller builds executables for all five scripts on each operating system.
4. The built executables are uploaded as artifacts.
5. A new GitHub Release is automatically created and tagged with the current timestamp, attaching all the cross-platform executables as downloadable assets.
