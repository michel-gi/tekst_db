# TekstDB Project

A collection of Python tools for managing a simple, indexed, text-based database. This project features a graphical user interface and several console-based applications for creating, editing, and testing the database.

## Features

This project consists of several standalone applications:

### GUI Application

* **`tekstdb_gui`**: A graphical user interface for managing the text database. It allows for creating, opening, saving, adding, editing, and deleting text entries.

### Console Applications

* **`tekstdb_bewerk`**: A command-line tool for managing the text-based database (`database.py`).
* **`tekstdb_tester`**: A utility to test the integrity and functionality of the text database.
* **`rapport.py`**: An example script demonstrating how to use the `TextDatabase` class to read data and generate a simple report.

## Core Component: `database.py` - The Text Database

At the heart of the applications in this project is a simple, custom-built text database managed by the `TextDatabase` class in `database.py`.

* **Purpose**: To provide a lightweight, human-readable way to store and manage indexed blocks of text in a single file.
* **Format**: It uses a simple format where each entry is preceded by a unique `###INDEX: <number>` marker.
* **Functionality**: The class handles all the necessary operations:
  * Reading and parsing the database file.
  * Adding, modifying, and deleting entries.
  * Automatically re-indexing entries to maintain a compact index.
* **Usage**: This component is used by the `tekstdb_gui`, `tekstdb_bewerk`, and `tekstdb_tester` applications to manage and verify the data.

## Getting Started

The easiest way to use these tools is to download the pre-built executables for your operating system from the project's GitHub Releases page.

1. Go to the [**Releases**](https://github.com/[your-github-username]/[your-repo-name]/releases) page of this repository.
2. Find the latest release and download the executables for your operating system (Windows, macOS, or Linux).

### Running the Applications

* **Windows**: Download the `.exe` file and double-click it to run.
* **macOS / Linux**: Download the executable file. You may need to make it executable before running it from your terminal:

```bash
# Example for the GUI on Linux
chmod +x ./tekstdb_gui-linux
./tekstdb_gui-linux
```

## Building from Source

If you prefer to build the applications yourself, you can do so by following these steps.

### Prerequisites

* Python 3.12
* Git

### Steps

1. **Clone the repository:**

    ```bash
    git clone https://github.com/[your-github-username]/tekst_db.git
    cd tekst_db
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
    # For the GUI application
    pyinstaller --onefile --windowed tekstdb_gui.py

    # For a console application
    pyinstaller --onefile --console tekstdb_bewerk.py
    ```

    The resulting executable will be located in the `dist/` directory.

## Continuous Integration

This project uses GitHub Actions for Continuous Integration and Continuous Deployment (CI/CD). On every push to the `main` branch, the following automated process is triggered:

1. Jobs are initiated for Windows, macOS, and Linux environments.
2. All Python dependencies from `requirements.txt` are installed.
3. PyInstaller builds executables for all five scripts on each operating system.
4. The built executables are uploaded as artifacts to a new GitHub Release.
5. The release is automatically tagged with the current timestamp, making all cross-platform executables available as downloadable assets.
