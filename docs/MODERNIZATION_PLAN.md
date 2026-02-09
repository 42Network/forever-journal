# Forever Journal Modernization Plan
**Date:** February 9, 2026
**Status:** In Progress (Branch: `refactor-modernization`)

## 1. Vision & Philosophy
The goal is to transform the original single-script prototype (`forever_journal.py`) into a robust, object-oriented application. The project adheres to two core philosophies:
1.  **Analogue Backup / Self-Replicating:** The physical book must contain its own source code in the appendix, allowing a future user to re-generate or modify the software even if the digital repository is lost.
2.  **Zero-Install Accessibility:** While retaining power tools for developers, we enable non-technical users to generate their own journals using cloud infrastructure (GitHub Actions) without installing Python or LaTeX locally.

## 2. User Personas & Distribution Strategy

| Persona | Method | Workflow | Pros/Cons |
| :--- | :--- | :--- | :--- |
| **The Author (Nathan)** | **Local Dev** | Uses extensive local Python setup. Prints on specific hardware (HP 9015) enabling "Bleed" features (Edge Index). | **Pro:** Fast iteration, premium physical output. <br>**Con:** "Works on my machine" fragility. |
| **The Tech Friend** | **Docker / Local** | Clones repo, runs `docker-compose up` or `pip install`. Comfortable exploring YAML/Code. | **Pro:** Clean environment, customizable. <br>**Con:** Requires 4GB+ Docker download. |
| **The Non-Tech User** | **GitHub Actions** | Forks repo on GitHub web. Edits `user_data.yaml` in browser. Clicks "Run Workflow". Downloads PDF artifact. | **Pro:** Zero install. "Profile" system ensures safe margins. <br>**Con:** Requires GitHub account. |

## 3. Technical Architecture

### A. Configuration Separation
We decouple **Personal Data** from **Hardware Constraints**.
*   `config/user_data.yaml`: Contains strictly personal info (Start Year, Birthdays, Anniversaries, Special Events like "Japan Fukuoka Mission").
*   `config/printer_profiles.yaml`: Contains hardware-specific settings.
    *   **Bleed Mode:** Controls if the "Edge Index" tabs touch the physical paper edge (0mm) or are inset (5mm) for standard printers.
    *   **Profiles:** `hp9015_nathan`, `default_a4`, `default_letter`.

### B. The Application Stack
*   **CLI:** `Typer` for a robust command-line interface.
*   **Data Validation:** `Pydantic` models ensure dates are valid and config is well-formed before starting the expensive PDF render.
*   **Templating:** `Jinja2` (`.tex.j2` files) separates Python logic from LaTeX presentation.
*   **Archival:** `Dockerfile` freezes the specific Python + TeXLive environment for long-term reproducibility.

### C. Self-Replication (The Appendix)
The original script simply printed itself. The new version must be smarter:
*   **Recursive File Walker:** The generator will iterate through `src/`, `config/`, and `templates/`.
*   **Formatting:** Each file is rendered into a LaTeX `lstlisting` block in the Appendix.
*   **Result:** The printed book contains the *entire* codebase, not just the logic script.

## 4. Work Accomplished (Session: Feb 9, 2026)

*   **Branch:** Created `refactor-modernization`.
*   **Structure:**
    *   `legacy/`: Archived original `forever_journal_v1.py`.
    *   `src/`: Created module structure (`models.py`, `utils.py`, `generator.py`, `renderer.py`).
    *   `config/`: Established YAML config pattern.
*   **Configuration:**
    *   Migrated all hardcoded special days (Birthdays, Holidays, Missions) to `config/user_data.yaml`.
    *   Defined `config/printer_profiles.yaml` with support for "Safe" vs "Bleed" edge indexing.
*   **Infrastructure:**
    *   Created `Dockerfile` for the "Time Capsule" requirement.
    *   Created `run.py` entry point.
    *   Defined `requirements.txt`.

## 5. Roadmap: Phase 2 (Target: End of February)

**Goal:** Complete the migration so the March production print can be done using the new system.

1.  **Template Migration:**
    *   Refactor the massive `generate_tex` strings from the legacy script into clean `templates/*.tex.j2` files.
    *   Prioritize `daily_page.tex.j2` and `yearly_summary.tex.j2` (ensure the recently fixed text wrapping logic is preserved!).

2.  **Logic Implementation (`src/generator.py`):**
    *   Port the date calculation and loop logic.
    *   Connect the `Pydantic` models to the Jinja2 context.

3.  **Self-Replication Engine:**
    *   Write the logic to crawl the new directory structure and generate the Appendix.

4.  **Validation:**
    *   Generate a PDF using the new system.
    *   **Visual Regression:** Compare purely against the "Golden Master" (February Legacy PDF) to ensure no regressions in layout or date math.
