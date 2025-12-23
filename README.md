# Forever Journal (2026–2035)

A Python and LaTeX project to generate a custom, archival-quality 10-Year Journal.

## Project Goal
To engineer a "Forever Journal" layout that fits 10 years of daily entries onto A4 paper, designed for binding in a high-quality Japanese binder (e.g., Maruman Giuris).

## Physical Specifications
*   **Format:** A4 Size (210mm x 297mm)
*   **Binding:** 30-Hole System (requires specific inner margins)
*   **Paper:** Recommended Maruman 80gsm A4 Loose Leaf or Kokuyo KB 64gsm.
*   **Capacity:** Approx. 100 sheets total (Double-sided printing).

## Layout Specifications
*   **Density:** 4 Days per Spread (2 Days per Page).
*   **Columns:** Page is split into 2 vertical columns.
*   **Rows:** Each column contains **10 Year Blocks** (2026–2035).
*   **Writing Space:** 5 lines per year block.
*   **Margins:** Mirror Margins (Inner gutter shift) to accommodate hole punching.
*   **Alignment:** Mirrored layout (Day labels align to the outer edge of the page).

## Tech Stack
*   **Logic:** Python 3 (`forever_journal.py`)
    *   Handles date iteration (leap years).
    *   Calculates "Day of Week" for 10 years.
    *   Generates raw `.tex` content.
    *   **Auto-compiles** to PDF if `pdflatex` is found.
*   **Rendering:** LaTeX (`pdflatex`)
    *   `geometry`: For precise A4 dimensions and mirror margins.
    *   `tikz`: For drawing writing lines, grids, and guide circles.

## Requirements
*   Python 3.x
*   LaTeX Distribution (e.g., TeX Live, MacTeX) with `pdflatex`.

## Usage

### 1. Generate & Compile
Run the script. It will generate the LaTeX file in `output/` and automatically compile it to PDF if `pdflatex` is installed.

```bash
# Standard Generation (Full Journal)
python3 forever_journal.py --spread 4up --align mirrored

# Test Mode (Generates a small subset of pages for testing layout)
python3 forever_journal.py --test --spread 4up --align mirrored
```

### 2. Options
*   `--no-compile`: Skip the automatic PDF compilation step.
*   `--test`: Generate a small test file (12 pages) instead of the full journal.

### 3. Manual Compilation
If you skip compilation or don't have `pdflatex` in your PATH, you can compile manually:

```bash
pdflatex -output-directory output output/forever_journal_2026_2035.tex
```

## Printing Tips & Troubleshooting

### Printer Settings
*   **Scale:** Always print at **100% Scale**. Do not select "Fit to Page" or "Scale to Fit", as this will distort the carefully calculated margins and line heights.
*   **Paper Size:** If your printer supports it, select **"A4 Borderless"** (or your specific paper size's borderless option). Standard driver settings often enforce a ~5mm non-printable margin that can clip the headers or footers of this edge-to-edge design.

### Pre-Punched Paper
If you are printing on pre-punched paper (e.g., Maruman/Kokuyo loose leaf):
1.  Run the script in **Test Mode** (`--test`) first.
2.  Print the short 12-page sample.
3.  Verify that the **Inner Margins** (the wider margins) align with the holes.
4.  This confirms you have the paper loaded in the correct orientation (holes on the left vs. right) before committing to the full print job.

### Margin Testing (`margin_test.py`)
If you are unsure about your printer's hardware margins or alignment:
1.  Run the included utility script:
    ```bash
    python3 margin_test.py
    pdflatex margin_test.tex
    ```
2.  This generates a grid overlay (`margin_test.pdf`).
3.  Print this page to measure exactly how close to the edge your printer can print and if there is any hardware offset (centering error) you need to account for.
