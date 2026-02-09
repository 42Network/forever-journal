# Forever Journal (2026–2035)

> **⚠️ Project Status: Modernization in Progress**
> *   **Stable Version (v1):** Located in `legacy/forever_journal_v1.py`. Use this for production printing (instructions below).
> *   **Modern Version (v2/v3):** Currently being refactored into a modular `src/` structure with `config/` files. See `docs/MODERNIZATION_PLAN.md` for details.

A Python and LaTeX project to generate a custom, archival-quality 10-Year Journal.

### 🌟 Key Differentiator: The "Reasonable Binder" Factor
Unlike other 5- or 10-year journals that require thick, heavy custom binding, **Forever Journal** is engineered to fit an entire decade (~366 days) onto just **~100 sheets of A4 paper**.
*   **4 Days per Spread:** By fitting 4 days on a single folded sheet (2 days front, 2 days back), the total thickness remains under 15mm.
*   **Standard Binders:** This allows the entire 10-year volume to fit comfortably into a high-quality standard **25mm loose-leaf binder** (like Maruman Giuris), making it portable and refillable.

## Project Goal
To engineer a "Forever Journal" layout that fits 10 years of daily entries onto A4 paper, designed for binding in a high-quality Japanese binder (e.g., Maruman Giuris).

## Physical Specifications
*   **Format:** A4 Size (210mm x 297mm)
*   **Binding:** 30-Hole System (requires specific inner margins)
*   **Paper:** Recommended Maruman 80gsm A4 Loose Leaf or Kokuyo KB 64gsm.
*   **Capacity:** **~100 sheets total**. This is the critical spec that allows a full decade to fit in standard 25mm binder rings.

## Layout Specifications
*   **Density:** 4 Days per Spread (2 Days per Page).
*   **Columns:** Page is split into 2 vertical columns.
*   **Rows:** Each column contains **10 Year Blocks** (2026–2035).
*   **Writing Space:** 6 lines per year block.
*   **Margins:** Mirror Margins (Inner gutter shift) to accommodate hole punching.
*   **Alignment:** Mirrored layout (Day labels align to the outer edge of the page).
*   **Thickness:** Automatically calculated and displayed in info box. Varies with page count.

## Features (v2.0)
The journal generator includes rigorous checks for rigorous writers:
*   **Whimsy Icons**: Special events (Birthdays, Holidays) are prefixed with relevant FontAwesome icons and colors (e.g., Red Heart for Valentine's, Green Clover for St. Patrick's).
*   **Kanji Support**: Days of the week include Japanese Kanji abbreviations (月, 火, 水...) for bilingual utility.
*   **Hyperlinked ToC**: The Title Page includes a generated Table of Contents with clickable links to the title page, every Month Summary, Event Lists, and the Source Code appendix.
*   **Sanitized Source Code Include**: The `--include-source` option properly handles multi-byte characters (like Kanji) by replacing them with Unicode placeholders, preventing LaTeX compilation crashes.
*   **Edge Indexing**: Black navigation tabs bleed to the outer edge of every page for quick month access by thumbing the side of the book. Tabs are visible even when the book is closed.

## Printer Settings & Margins
For the most accurate reproduction of the layout, especially the **Edge Index Tabs**, correct printer settings are mandatory.

| Setting | Value | Reason |
| :--- | :--- | :--- |
| **Scaling** | **100%** (Actual Size) | "Scale to Fit" shrinks the line heights (designed for 6mm hand-writing) and corrupts the hole-punch margins. |
| **Borderless** | **ON** | **Required** for Edge Index Tabs. Without this, tabs will have a white gap at the paper edge. |
| **Extension** | **Min/Least** | When Borderless is ON, printers "zoom" the page. Set extension to minimum to prevent cutting off text near the edge. |
| **Media Type** | **Inkjet Paper** (or Matte) | Tells the printer to assume a higher quality surface, often improving alignment accuracy. |

### Years vs Writing Area
The script dynamically calculates writing space based on paper size margins. The number of years chosen inversely affects the writing space per day. Calculated for A4 Paper with standard margins:

| Years | Lines/Day | Line Spacing | Notes |
| :--- | :---: | :---: | :--- |
| **8 Years** | 6 | ~5.8 mm | Comfortable, standard rule. |
| **9 Years** | 6 | ~5.1 mm | Compact rule, good for fine pens (0.38mm). |
| **10 Years** | 5 | ~6.0 mm | Reduces line count to maintain spacing. |
| **10 Years** | 6 | ~4.7 mm | Very tight. Requires precision writing. |

## Tech Stack
*   **Logic:** Python 3
    *   **Legacy:** `legacy/forever_journal_v1.py` (Single-script architecture).
    *   **Modern:** `src/` modules (in progress).
    *   Handles date iteration (leap years).
    *   Calculates "Day of Week" for 10 years.
    *   Generates raw `.tex` content.
    *   **Auto-compiles** to PDF if `pdflatex` is found.
*   **Rendering:** LaTeX (`pdflatex`)
    *   `geometry`: For precise A4 dimensions and mirror margins.
    *   `tikz`: For drawing writing lines, grids, and guide circles.
    *   `xcolor`: Uses **CMYK** color model for accurate print reproduction (especially red).

## Requirements
*   Python 3.x
*   LaTeX Distribution (e.g., TeX Live, MacTeX) with `pdflatex`.
*   LaTeX Packages: `geometry`, `tikz`, `fancyhdr`, `fontawesome5` (for whimsy mode).

## Usage

### 1. Generate & Compile (Legacy v1)
The stable version of the generator has been moved to the `legacy/` directory. Run the script from the project root.

```bash
# Standard Generation (Full Journal)
python3 legacy/forever_journal_v1.py --spread 4up --align mirrored

# Whimsy Mode (Adds icons and colors to special days)
python3 legacy/forever_journal_v1.py --spread 4up --align mirrored --whimsy

# Test Mode (Generates a small subset of pages for testing layout)
# Captures: Title, Feb Summary, Feb 1-4, Feb 29, YM1, Dec 29-31, Extra Pages, Source Code.
python3 legacy/forever_journal_v1.py --test --spread 4up --align mirrored
```

### 2. Options
*   `--no-compile`: Skip the automatic PDF compilation step.
*   `--include-source`: Append the source code of the script to the end of the PDF.
*   `--toc`: Include a Table of Contents on the Title Page (requires 2-pass compilation).
*   `--single-pass`: Run `pdflatex` only once. Faster for quick checks, but Edge Indexing and ToC references may be incorrect.

## Special Day Annotations
The journal supports annotating special days (Holidays, Birthdays, Anniversaries) directly into the writing grid. These are configured in the `SPECIAL_DAYS` dictionary within `legacy/forever_journal_v1.py`.

### Configuration
Edit the `SPECIAL_DAYS` dictionary at the top of `legacy/forever_journal_v1.py`:

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
    "birthdays": [
        # Calculates "Years Since" (e.g., "Nathan (58y)")
        {"name": "Nathan", "date": "1968-11-29"},
    ],
    "anniversaries": [
        {"name": "Nathan & Dana", "date": "1994-06-30"},
    ]
}
```

### Features
*   **Annual Events:** Supports fixed dates (Month/Day) and variable rules (Nth Weekday of Month, Easter).
*   **Counting Events:** Automatically calculates the age or anniversary year for the specific journal year (e.g., in 2026, a 1996 birthday shows as "(30y)").
*   **Title Page Summary:** A table of all configured special days is generated on the Title Page, including current age/years for birthdays and anniversaries.
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


### Paper & Print Calibration
To ensure the 10-year archival quality of the journal and prevent paper deformation, use the following settings on the HP OfficeJet Pro 9015:

Test Prints (Kokuyo KB 64gsm): * Settings: Media: Plain Paper | Quality: Draft

Reason: The 64gsm density is significantly lighter than standard US copy paper. Draft mode reduces ink volume, preventing the paper from curling or "cockling" during the print cycle.

Final Journal (Kokuyo Campus Sarasara): * Settings: Media: Specialty Paper, Matte | Quality: Normal

Reason: Sarasara paper (75-77gsm) handles "Normal" ink loads well, but the Specialty Matte profile optimizes the print head pass speed. This ensures the ink sets correctly on the smooth Japanese finish without smearing, which is vital for double-sided journaling.