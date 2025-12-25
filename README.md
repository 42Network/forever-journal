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
# Captures: Title, Feb Summary, Feb 1-4, Feb 29, YM1, Dec 29-31, Extra Pages, Source Code.
# Preserves even/odd page alignment for double-sided printing.
python3 forever_journal.py --test --spread 4up --align mirrored
```

### 2. Options
*   `--no-compile`: Skip the automatic PDF compilation step.
*   `--include-source`: Append the source code of the script to the end of the PDF.
*   `--toc`: Include a Table of Contents on the Title Page (requires 2-pass compilation).

## Special Day Annotations
The journal supports annotating special days (Holidays, Birthdays, Anniversaries) directly into the writing grid. These are configured in the `SPECIAL_DAYS` dictionary within `forever_journal.py`.

### Configuration
Edit the `SPECIAL_DAYS` dictionary at the top of `forever_journal.py`:

```python
SPECIAL_DAYS = {
    "annual": [
        # Fixed Date
        {"name": "New Year's Day", "month": 1, "day": 1},
        # Variable Rule (e.g., 3rd Monday in Feb)
        {"name": "President's Day", "rule": "3rd Mon Feb"},
        # Special Rules
        {"name": "Easter", "rule": "easter"},
    ],
    "counting": [
        # Calculates "Years Since" (e.g., "Nathan (58y)")
        {"name": "Nathan", "type": "Birthday", "date": "1968-11-29"},
        {"name": "Nathan & Dana", "type": "Anniversary", "date": "1994-06-30"},
    ]
}
```

### Features
*   **Annual Events:** Supports fixed dates (Month/Day) and variable rules (Nth Weekday of Month, Easter).
*   **Counting Events:** Automatically calculates the age or anniversary year for the specific journal year (e.g., in 2026, a 1996 birthday shows as "(30y)").
*   **Title Page Summary:** A table of all configured special days is generated on the Title Page.
*   **Grid Injection:** The event name is printed in small text on the first line of the daily block, carefully aligned to avoid writing guides.

## Extra Pages
The journal includes a section of **Extra Pages** at the end (default: 10 pages) for longer entries that overflow the daily grid.
*   **Layout:** 2-Column layout matching the daily pages.
*   **Header:** "Extra Pages" header aligned to the outer edge.
*   **Annotation:** A small "*date*" prompt at the top of each column to encourage dating entries.
*   **Pagination:** Dynamically calculated to ensure the Source Code appendix always starts on a fresh sheet (Odd page).

## Test Mode Requirements
The `--test` flag generates a representative subset of the journal to verify layout and printing alignment without generating the full 400+ pages.
*   **Title Page:** Page 1 (Odd).
*   **February Summary:** 2-page spread (Even/Odd).
*   **February Start:** Days 1-4 (Even/Odd spread).
*   **February End:** Day 29 (Leap Year check) + Year/Month Summary (YM1).
*   **December End:** Days 29-31 (End of Journal).
*   **Extra Pages:** First spread (1-2) and Last page (10).
*   **Source Code:** Full appendix.
*   **Alignment:** Strictly preserves Even/Odd (Left/Right) page parity for correct double-sided printing.
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
