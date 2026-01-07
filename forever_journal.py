"""
Forever Journal Generator
------------------------
Generates a multi-year journal layout in LaTeX format.
Designed for A4 paper with specific margin requirements for hole punching.

Usage:
    python forever_journal.py [options]

Options:
    --num-years N       Number of years to track (default: 10)
    --num-lines N       Number of writing lines per block (default: 5)
    --spread MODE       Layout mode: '2up' (1 day/page) or '4up' (2 days/page) (default: 2up)
    --align MODE        Alignment: 'mirrored' (outer) or 'left' (default: mirrored)
    --whimsy            Add icons and colors to special days
    --kanji             Add Japanese Kanji to day labels
    --toc               Include Table of Contents
    --event-lists       Enable Event List filler pages
    --test              Generate a small subset of pages for testing
    --no-compile        Skip automatic PDF compilation
    --single-pass       Run pdflatex only once (faster, but refs may be broken)
    --include-source    Append source code to the PDF
"""

import datetime
import calendar
import argparse
import os
import shutil
import subprocess

# --- CONFIGURATION: JOURNAL SETTINGS ---
START_YEAR = 2026
NUM_YEARS = 10
NUM_WRITING_LINES = 5
SUNDAYS_RED = True
OUTPUT_DIR = "output"

# --- CONFIGURATION: PAPER & MARGINS ---
# Paper Sizes (mm)
PAPER_SIZES = {
    "US_LETTER": {"w": 215.9, "h": 279.4},
    "JIS_B5":    {"w": 182.0, "h": 257.0},
    "A4":        {"w": 210.0, "h": 297.0}
}

CURRENT_PAPER_KEY = "A4"
PAPER = PAPER_SIZES[CURRENT_PAPER_KEY]

# Physical Margins (mm)
# Bottom margin set to 10mm to prevent printer cutoff
TARGET_MARGIN_INNER = 13
TARGET_MARGIN_OUTER = 9
TARGET_MARGIN_TOP = 5
TARGET_MARGIN_BOTTOM = 10

PAGE_W = PAPER["w"]
PAGE_H = PAPER["h"]

# --- CONFIGURATION: LAYOUT DIMENSIONS ---
# Text Width = Page Width - Inner - Outer
CALC_TEXT_WIDTH = PAGE_W - TARGET_MARGIN_INNER - TARGET_MARGIN_OUTER

# Header height reserved for Day/Month display
HEADER_H = 6

# Width reserved for the Year/Day label column
YEAR_LABEL_WIDTH = 10

# Vertical spacing adjustment for labels to avoid touching the line above
LABEL_Y_SHIFT = -0.8

# Calculate Block Height
# We estimate usable height based on margins to keep layout consistent
ESTIMATED_TEXT_HEIGHT = PAGE_H - TARGET_MARGIN_TOP - TARGET_MARGIN_BOTTOM
USABLE_H = ESTIMATED_TEXT_HEIGHT - HEADER_H - 2
BLOCK_H = USABLE_H / NUM_YEARS


# --- CONFIGURATION: SPECIAL DAYS ---
SPECIAL_DAYS = {
    "annual": [
        {"name": "New Year's Day", "month": 1, "day": 1},
        {"name": "MLK Day", "rule": "3rd Mon Jan"},
        {"name": "Valentine's Day", "month": 2, "day": 14},
        {"name": "President's Day", "rule": "3rd Mon Feb"},
        {"name": "St. Patrick's Day", "month": 3, "day": 17},
        {"name": "Easter", "rule": "easter"},
        {"name": "Mother's Day", "rule": "2nd Sun May"},
        {"name": "Memorial Day", "rule": "last Mon May"},
        {"name": "Father's Day", "rule": "3rd Sun Jun"},
        {"name": "Juneteenth", "month": 6, "day": 19},
        {"name": "Independence Day", "month": 7, "day": 4},
        {"name": "Labor Day", "rule": "1st Mon Sep"},
        {"name": "Columbus Day", "rule": "2nd Mon Oct"},
        {"name": "Halloween", "month": 10, "day": 31},
        {"name": "Election Day", "rule": "election"},
        {"name": "Veterans Day", "month": 11, "day": 11},
        {"name": "Thanksgiving", "rule": "4th Thu Nov"},
        {"name": "Christmas", "month": 12, "day": 25},
    ],
    "birthdays": [
        {"name": "Nathan", "date": "1968-11-29"},
        {"name": "Dana", "date": "1968-09-26"},
        {"name": "Benjamin", "date": "1995-08-18"},
        {"name": "Thaddeus", "date": "1996-11-30"},
        {"name": "Eli", "date": "2000-03-30"},
        {"name": "Isaac", "date": "2003-08-28"},
        {"name": "Lydia", "date": "2005-01-19"},
        {"name": "Keren", "date": "2007-09-11"},
        {"name": "Aaron", "date": "1971-02-28"},
        {"name": "Esther", "date": "1973-01-24"},
        {"name": "Rachel", "date": "1975-08-16"},
        {"name": "Beth", "date": "1978-10-07"},
        {"name": "Sarah", "date": "1984-03-26"},
        {"name": "Bill", "date": "1943-03-09"},
        {"name": "Pat", "date": "1945-04-15"},
        {"name": "Keith", "date": "1949-10-25"},
        {"name": "Judy", "date": "1950-11-26"},
        {"name": "Amy", "date": "1971-04-19"},
        {"name": "Monique", "date": "1996-09-28"},
        {"name": "Luci & True", "date": "2023-03-21"},
        {"name": "Tommy", "date": "2024-07-23"},
        {"name": "Thaddeus II", "date": "2025-10-11"},
    ],
    "anniversaries": [
        {"name": "Nathan & Dana", "date": "1994-06-30"},
        {"name": "Bill & Pat", "date": "1967-07-07"},
        {"name": "Keith & Judy", "date": "1967-11-18"},
        {"name": "Ben & Mo", "date": "2019-08-02"},
        {"name": "Tad & Missa", "date": "2022-12-21"},
        {"name": "Aub & Tom", "date": "2024-08-16"},
    ]
}

KANJI_DAYS = {
    "Mon": "月",
    "Tue": "火",
    "Wed": "水",
    "Thu": "木",
    "Fri": "金",
    "Sat": "土",
    "Sun": "日"
}

def calculate_easter(year):
    """Calculates Western Easter date for a given year."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return month, day

def calculate_election_day(year):
    """Calculates US Election Day (Tuesday after the first Monday in November)."""
    # Get 1st Monday of November (Month 11, Weekday 0)
    first_monday = get_nth_weekday_of_month(year, 11, 0, 1)
    # Election Day is the next day (Tuesday)
    return 11, first_monday + 1

def get_nth_weekday_of_month(year, month, weekday_idx, n):
    """
    Returns the day of the month for the Nth occurrence of a weekday.
    weekday_idx: 0=Mon, 6=Sun
    n: 1 for 1st, 2 for 2nd, ... -1 for last
    """
    cal = calendar.monthcalendar(year, month)
    days = [week[weekday_idx] for week in cal if week[weekday_idx] != 0]
    if n > 0:
        if n <= len(days):
            return days[n-1]
    else:
        if abs(n) <= len(days):
            return days[n]
    return None

def parse_rule(rule, year):
    """Parses a rule string like '3rd Mon Feb' and returns (month, day)."""
    parts = rule.split()
    if rule == "easter":
        return calculate_easter(year)
    if rule == "election":
        return calculate_election_day(year)
    
    if len(parts) == 3:
        # e.g. "3rd Mon Feb" or "last Mon May"
        nth_str, day_str, month_str = parts
        
        # Parse Month
        month_map = {m: i for i, m in enumerate(calendar.month_abbr) if m}
        month = month_map.get(month_str[:3].title())
        if not month: return None, None
        
        # Parse Weekday
        day_map = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
        weekday = day_map.get(day_str[:3].title())
        if weekday is None: return None, None
        
        # Parse Nth
        if nth_str.lower() == "last":
            n = -1
        else:
            # "1st", "2nd", "3rd", "4th"
            n = int(nth_str[0])
            
        day = get_nth_weekday_of_month(year, month, weekday, n)
        return month, day
        
    return None, None

def get_special_events(year, month, day, use_whimsy=False):
    events = []
    
    # Check Annual
    for item in SPECIAL_DAYS["annual"]:
        if "month" in item and "day" in item:
            if item["month"] == month and item["day"] == day:
                name = item["name"]
                if use_whimsy and name in WHIMSY_STYLES:
                    style = WHIMSY_STYLES[name]
                    name = rf"\textcolor{{{style['color']}}}{{{style['icon']} {name}}}"
                events.append(name)
        elif "rule" in item:
            m, d = parse_rule(item["rule"], year)
            if m == month and d == day:
                name = item["name"]
                if use_whimsy and name in WHIMSY_STYLES:
                    style = WHIMSY_STYLES[name]
                    name = rf"\textcolor{{{style['color']}}}{{{style['icon']} {name}}}"
                events.append(name)
                
    # Check Birthdays
    for item in SPECIAL_DAYS["birthdays"]:
        # Parse date "YYYY-MM-DD"
        y_str, m_str, d_str = item["date"].split("-")
        if int(m_str) == month and int(d_str) == day:
            years_elapsed = year - int(y_str)
            if years_elapsed >= 0:
                name = item['name']
                
                if use_whimsy:
                    style = WHIMSY_STYLES.get("Birthday")
                    if style:
                        name = rf"\textcolor{{{style['color']}}}{{{style['icon']} {name}}}"
                
                events.append(f"{name} ({years_elapsed}y)")

    # Check Anniversaries
    for item in SPECIAL_DAYS["anniversaries"]:
        # Parse date "YYYY-MM-DD"
        y_str, m_str, d_str = item["date"].split("-")
        if int(m_str) == month and int(d_str) == day:
            years_elapsed = year - int(y_str)
            if years_elapsed >= 0:
                name = item['name']
                
                if use_whimsy:
                    style = WHIMSY_STYLES.get("Anniversary")
                    if style:
                        name = rf"\textcolor{{{style['color']}}}{{{style['icon']} {name}}}"
                
                events.append(f"{name} ({years_elapsed}y)")
                
    return events


def get_day_of_week(year, month, day):
    """Returns the abbreviated day of the week (e.g., 'Mon') for a given date."""
    try:
        dt = datetime.date(year, month, day)
        return dt.strftime("%a")
    except ValueError:
        return ""

# --- WHIMSY CONFIGURATION ---
WHIMSY_STYLES = {
    "New Year's Day": {"icon": r"\faGlassCheers", "color": "purple"},
    "MLK Day": {"icon": r"\faHandsHelping", "color": "black"},
    "Valentine's Day": {"icon": r"\faHeart", "color": "magenta"},
    "President's Day": {"icon": r"\faFlagUsa", "color": "blue"},
    "St. Patrick's Day": {"icon": r"\faLeaf", "color": "green"}, # Leaf as Shamrock
    "Easter": {"icon": r"\faEgg", "color": "violet"},
    "Mother's Day": {"icon": r"\faHeart", "color": "pink"},
    "Memorial Day": {"icon": r"\faFlagUsa", "color": "blue"},
    "Father's Day": {"icon": r"\faUserTie", "color": "blue"},
    "Juneteenth": {"icon": r"\faStar", "color": "black"},
    "Independence Day": {"icon": r"\faStar", "color": "blue"},
    "Labor Day": {"icon": r"\faHammer", "color": "brown"},
    "Columbus Day": {"icon": r"\faShip", "color": "blue"},
    "Halloween": {"icon": r"\faGhost", "color": "orange"},
    "Election Day": {"icon": r"\faVoteYea", "color": "blue"},
    "Veterans Day": {"icon": r"\faMedal", "color": "olive"},
    "Thanksgiving": {"icon": r"\faUtensils", "color": "brown"},
    "Christmas": {"icon": r"\faTree", "color": "red"},
    "Birthday": {"icon": r"\faBirthdayCake", "color": "teal"},
    "Anniversary": {"icon": r"\faRing", "color": "orange"},
}

def generate_tex(test_mode=False, spread_mode="2up", align_mode="mirrored", no_compile=False, include_source=False, toc_enabled=False, whimsy=False, single_pass=False, event_lists_enabled=False, kanji_enabled=False, num_years=10, num_writing_lines=5):
    """
    Generates the LaTeX source file for the journal.

    Args:
        test_mode (bool): If True, generates a small subset of pages for testing.
        spread_mode (str): "2up" (1 day/page) or "4up" (2 days/page).
        align_mode (str): "mirrored" (outer alignment) or "left" (standard alignment).
        no_compile (bool): If True, skips automatic PDF compilation.
        include_source (bool): If True, appends the script source code to the PDF.
        toc_enabled (bool): If True, includes a Table of Contents.
        whimsy (bool): If True, adds icons and colors to special days.
        single_pass (bool): If True, runs pdflatex only once (faster, but references/overlays may be broken).
        event_lists_enabled (bool): If True, generates Event List pages as filler.
        kanji_enabled (bool): If True, adds Japanese Kanji to day labels.
        num_years (int): Number of years to track (default 10).
        num_writing_lines (int): Number of writing lines per block (default 5).
    """
    # Shadow globals with arguments
    NUM_YEARS = num_years
    NUM_WRITING_LINES = num_writing_lines

    # Recalculate Block Height based on dynamic years
    USABLE_H = ESTIMATED_TEXT_HEIGHT - HEADER_H - 2
    BLOCK_H = USABLE_H / NUM_YEARS

    end_year = START_YEAR + NUM_YEARS - 1
    output_base = f"forever_journal_{START_YEAR}_{end_year}"
    if test_mode:
        output_base = f"test_{output_base}"
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_tex = os.path.join(OUTPUT_DIR, f"{output_base}.tex")

    # Determine Days Per Page
    DAYS_PER_PAGE = 2 if spread_mode == "4up" else 1

    # Test Mode Logic
    # We define a helper to check if content should be generated based on context.
    # We also track physical pages to ensure parity alignment.
    
    # Global counter for physical pages written to the PDF
    # Initialized to 0. Writing Title Page (Page 1) makes it 1.
    physical_page_count = 0
    event_list_counter = 1

    def draw_edge_index(month_idx):
        """Draws the edge index tab for the given month."""
        month_name = calendar.month_name[month_idx].upper()
        
        # Calculate vertical position
        # Respect Top and Bottom Margins
        tab_area_height = PAGE_H - TARGET_MARGIN_TOP - TARGET_MARGIN_BOTTOM
        segment_height = tab_area_height / 12
        
        # Start from Top Margin
        # Note: yshift is negative downwards from North East/West
        y_shift = - TARGET_MARGIN_TOP - (month_idx - 1) * segment_height
        
        # Determine side based on parity of the CURRENT page being written
        # We use physical_page_count + 1 because physical_page_count tracks pages *already written*
        # So the current page is physical_page_count + 1
        current_physical_page = physical_page_count + 1
        is_odd = (current_physical_page % 2 != 0)
        
        f.write(r"\begin{tikzpicture}[remember picture, overlay]" + "\n")
        
        # Box Width: Leave 1mm gap between tab and text body
        # TARGET_MARGIN_OUTER is 6mm, so box is 5mm.
        box_width = TARGET_MARGIN_OUTER - 1
        
        # Text Alignment: "Bottom Justified" (Aligned to Inner Edge/Spine)
        # We use \hspace to push the centered text towards the spine.
        # Box is 5mm. Text is centered. We want it flush with the inner edge.
        # Adding space to the "top" (outer edge) of the rotated text pushes it "down" (inner edge).
        spacer = r"\hspace*{1.5mm}" 
        
        if is_odd:
            # Right Page -> Right Edge (North East)
            # Text rotated -90 (Top to Bottom). Bottom of letters is West (Inner).
            # We want to push text West. Node centers content.
            # Content = [Text + Spacer]. Center is shifted Right. Text is shifted Left (West).
            content = rf"\rotatebox{{-90}}{{\sffamily\bfseries\small {month_name}}}{spacer}"
            f.write(rf"  \node[fill=black, text=white, anchor=north east, minimum width={box_width}mm, minimum height={segment_height}mm, yshift={y_shift}mm, inner sep=0pt] at (current page.north east) {{{content}}};" + "\n")
        else:
            # Left Page -> Left Edge (North West)
            # Text rotated 90 (Bottom to Top). Bottom of letters is East (Inner).
            # We want to push text East. Node centers content.
            # Content = [Spacer + Text]. Center is shifted Left. Text is shifted Right (East).
            content = rf"{spacer}\rotatebox{{90}}{{\sffamily\bfseries\small {month_name}}}"
            f.write(rf"  \node[fill=black, text=white, anchor=north west, minimum width={box_width}mm, minimum height={segment_height}mm, yshift={y_shift}mm, inner sep=0pt] at (current page.north west) {{{content}}};" + "\n")
            
        f.write(r"\end{tikzpicture}" + "\n")

    def render_event_list(event_list_num, width=None):
        """Renders an Event List column or page."""
        if width is None:
            width = COL_WIDTH

        # Determine alignment based on current physical page
        # physical_page_count tracks pages *completed*. Current page is +1.
        current_page_num = physical_page_count + 1
        is_even_page = (current_page_num % 2 == 0)

        # Header
        f.write(rf"\begin{{minipage}}[t][{HEADER_H}mm]{{\textwidth}}")
        
        header_text = rf"\huge \textbf{{Event List {event_list_num}}}"
        
        if is_even_page:
            # Left Page: Left Aligned
            f.write(rf"{header_text} \hfill")
        else:
            # Right Page: Right Aligned
            f.write(rf"\hfill {header_text}")
            
        f.write(r"\end{minipage}")
        f.write(rf"\addcontentsline{{toc}}{{section}}{{Event List {event_list_num}}}")
        f.write(rf"\label{{sec:event_list_{event_list_num}}}" + "\n")
        f.write(r"\par \nointerlineskip")

        # 10 Year Blocks
        for y_idx in range(NUM_YEARS):
            curr_year = START_YEAR + y_idx
            
            f.write(rf"\begin{{tikzpicture}}[x=1mm, y=1mm, trim left=0mm, trim right={width}mm]" + "\n")
            w = width
            h = BLOCK_H
            f.write(rf"\path[use as bounding box] (0,0) rectangle ({w}, {h});" + "\n")
            
            # Year Label (Right aligned)
            f.write(rf"\node[anchor=north east, text width={YEAR_LABEL_WIDTH}mm, align=right, inner sep=0pt, yshift={LABEL_Y_SHIFT}mm] at ({w},{h}) {{\textbf{{{curr_year}}}}};" + "\n")
            
            # Column Headers (Date | Event | Date | Event | Date | Event)
            # 3 Groups
            pair_w = w / 3
            date_w = pair_w / 4
            
            # Group 1
            f.write(rf"\node[anchor=north west, inner sep=1pt, font=\scriptsize\itshape] at (0, {h}) {{date}};" + "\n")
            f.write(rf"\node[anchor=north west, inner sep=1pt, font=\scriptsize\itshape] at ({date_w}, {h}) {{event}};" + "\n")
            
            # Group 2
            f.write(rf"\node[anchor=north west, inner sep=1pt, font=\scriptsize\itshape] at ({pair_w}, {h}) {{date}};" + "\n")
            f.write(rf"\node[anchor=north west, inner sep=1pt, font=\scriptsize\itshape] at ({pair_w + date_w}, {h}) {{event}};" + "\n")

            # Group 3
            f.write(rf"\node[anchor=north west, inner sep=1pt, font=\scriptsize\itshape] at ({2 * pair_w}, {h}) {{date}};" + "\n")
            f.write(rf"\node[anchor=north west, inner sep=1pt, font=\scriptsize\itshape] at ({2 * pair_w + date_w}, {h}) {{event}};" + "\n")

            # Top Border (First block only)
            if y_idx == 0:
                f.write(rf"\draw[bordergray] (0, {h}) -- ({w}, {h});" + "\n")
            
            # Vertical Dividers
            # Group 1/2 separator
            f.write(rf"\draw[guidegray] ({pair_w}, 0) -- ({pair_w}, {h});" + "\n")
            
            # Group 2/3 separator
            f.write(rf"\draw[guidegray] ({2 * pair_w}, 0) -- ({2 * pair_w}, {h});" + "\n")
            
            # Writing Guidelines
            line_spacing = h / NUM_WRITING_LINES
            for l in range(1, NUM_WRITING_LINES):
                y_pos = h - l * line_spacing
                f.write(rf"\draw[guidegray, dash pattern=on 0.5pt off 1pt] (0, {y_pos}) -- ({w}, {y_pos});" + "\n")

            # Bottom Divider
            f.write(rf"\draw[bordergray] (0, 0) -- ({w}, 0);" + "\n")
            f.write(r"\end{tikzpicture}" + "\n")
            f.write(r"\par \nointerlineskip" + "\n")

    def ensure_parity(logical_page_num):
        """
        Inserts a blank filler page if the next physical page in the PDF
        does not match the even/odd parity of the target logical page number.
        """
        nonlocal physical_page_count
        nonlocal event_list_counter
        
        # Parity: 1 = Odd, 0 = Even
        target_parity = logical_page_num % 2
        next_physical_parity = (physical_page_count + 1) % 2
        
        if target_parity != next_physical_parity:
            # Always render a blank page for parity correction
            # Event Lists are now exclusively in the appendix if enabled
            f.write(r"\null\newpage" + "\n")
            
            physical_page_count += 1

    def is_test_content(section, month=None, day=None, page_idx=None):
        if not test_mode:
            return True
            
        if section == "TITLE":
            return True
        
        if section == "MONTH_SUMMARY":
            # Only Feb Summary
            return month == 2
            
        if section == "DAILY":
            if month == 2:
                # Feb 1-4
                if day in [1, 2, 3, 4]:
                    return True
                # Feb 29 (Leap check)
                if day == 29:
                    return True
            
            # Anniversary: June 30
            if month == 6 and day == 30:
                return True
                
            # Birthdays: Nov 29, 30
            if month == 11 and day in [29, 30]:
                return True

            if month == 12:
                # Dec 29-31
                if day in [29, 30, 31]:
                    return True
            return False
            
        if section == "YEAR_MONTH_SUMMARY":
            # Only the one after Feb (YM1)
            return month == 2
            
        if section == "EXTRA_PAGES":
            # First spread (0, 1) and Last page (19 or 20)
            if page_idx in [0, 1, 19, 20]:
                return True
            return False
            
        if section == "SOURCE":
            return True
            
        return False

    def should_write_page(page_num):
        # Deprecated in favor of is_test_content, but kept for compatibility 
        # with existing calls that haven't been migrated if any.
        # In this refactor, we will replace calls to this function.
        return True

    # Column Layout
    COLUMN_GUTTER = 2  # mm
    if DAYS_PER_PAGE == 2:
        COL_WIDTH = (CALC_TEXT_WIDTH - COLUMN_GUTTER) / 2
    else:
        COL_WIDTH = CALC_TEXT_WIDTH

    with open(output_tex, "w") as f:
        # --- PREAMBLE ---
        f.write(r"""
\documentclass[10pt,twoside]{article}
""")
        # Geometry setup:
        # footskip=1mm pulls footer up; with bottom=10mm, footer sits safely from edge.
        f.write(rf"\usepackage[paperwidth={PAGE_W}mm, paperheight={PAGE_H}mm, inner={TARGET_MARGIN_INNER}mm, outer={TARGET_MARGIN_OUTER}mm, top={TARGET_MARGIN_TOP}mm, bottom={TARGET_MARGIN_BOTTOM}mm, footskip=1mm]{{geometry}}" + "\n")

        f.write(r"""
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}
\usepackage[cmyk]{xcolor}
\usepackage{tikz}
\usepackage{fancyhdr}
\usepackage{listings} % For source code listing
\usepackage{pdflscape} % For landscape pages
\usepackage{multicol} % For multi-column layout
\usepackage{fontawesome5} % For icons (whimsy mode)
\usepackage{CJKutf8} % For Japanese Kanji
\usepackage{graphicx} % For scaling text

\pagestyle{fancy}
\fancyhf{} % clear all headers and footers
\renewcommand{\headrulewidth}{0pt}
\fancyfoot[C]{\itshape \small \thepage} % Italic page number in center footer

\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}
\raggedbottom % Prevent underfull vbox warnings and forced vertical stretching

\makeatletter
\newcommand{\eventlistrow}[1]{%
  \@ifundefined{r@sec:event_list_#1}{}{%
    Event List #1 & \pageref{sec:event_list_#1} \\%
  }%
}
\makeatother

% Color Definitions
\definecolor{guidegray}{cmyk}{0,0,0,0.4} % Darker guide lines
\definecolor{bordergray}{cmyk}{0,0,0,0.7} % Darker border lines
\definecolor{textgray}{cmyk}{0,0,0,0.6}   % Date labels
\definecolor{sundayred}{cmyk}{0,1,1,0} % Pure Red for Sundays

% Code Listing Colors
\definecolor{codegreen}{cmyk}{1,0,1,0.4}
\definecolor{codegray}{cmyk}{0,0,0,0.5}
\definecolor{codepurple}{cmyk}{0.29,1,0,0.18}
\definecolor{backcolour}{cmyk}{0,0,0.08,0.05}
\definecolor{framegray}{cmyk}{0,0,0,0.1}

\begin{document}
\begin{CJK*}{UTF8}{min}
""")

        # --- COVER PAGE ---
        if is_test_content("TITLE"):
            ensure_parity(1)
            f.write(r"\begin{titlepage}" + "\n")
            f.write(r"\label{sec:title}" + "\n")
            f.write(r"\centering" + "\n")
            
            # Title at Top
            f.write(r"{\Huge \textbf{Forever Journal} \par}" + "\n")
            f.write(r"\vspace{0.5cm}" + "\n")
            f.write(rf"{{\Large {START_YEAR} -- {START_YEAR + NUM_YEARS - 1} \par}}" + "\n")
            f.write(r"\vspace{1cm}" + "\n")
            
            # Two Columns: Special Days (Left) | ToC (Right)
            f.write(r"\begin{minipage}[t]{0.48\textwidth}" + "\n")
            f.write(r"\centering" + "\n")
            f.write(r"\textbf{Special Days} \par \vspace{2mm}" + "\n")
            f.write(r"{\scriptsize" + "\n")
            f.write(r"\begin{tabular}{ll}" + "\n")
            f.write(r"\textbf{Annual} & \textbf{Rule/Date} \\" + "\n")
            for item in SPECIAL_DAYS["annual"]:
                name = item['name']
                if whimsy and name in WHIMSY_STYLES:
                    style = WHIMSY_STYLES[name]
                    name = rf"\textcolor{{{style['color']}}}{{{style['icon']} {name}}}"

                if "rule" in item:
                    rule = item["rule"]
                else:
                    rule = f"{calendar.month_abbr[item['month']]} {item['day']}"
                f.write(rf"{name} & {rule} \\" + "\n")
            
            # Birthdays
            f.write(r"& \\" + "\n")
            f.write(r"\textbf{Birthdays} & \textbf{Date} \\" + "\n")
            
            today = datetime.date.today()

            # Sort Birthdays by Month, Day
            sorted_birthdays = sorted(SPECIAL_DAYS["birthdays"], key=lambda x: (int(x['date'].split('-')[1]), int(x['date'].split('-')[2])))
            
            for item in sorted_birthdays:
                name = item['name'].replace("&", r"\&")
                if whimsy:
                    style = WHIMSY_STYLES.get("Birthday")
                    if style:
                        name = rf"\textcolor{{{style['color']}}}{{{style['icon']} {name}}}"
                
                # Format Date: M D, Y
                dt = datetime.datetime.strptime(item['date'], "%Y-%m-%d")
                date_str = dt.strftime("%b %-d, %Y")
                
                # Calculate Age
                born = dt.date()
                age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))

                f.write(rf"{name} & {date_str} ({age}) \\" + "\n")

            # Anniversaries
            f.write(r"& \\" + "\n")
            f.write(r"\textbf{Anniversaries} & \textbf{Date} \\" + "\n")
            
            # Sort Anniversaries by Month, Day
            sorted_anniversaries = sorted(SPECIAL_DAYS["anniversaries"], key=lambda x: (int(x['date'].split('-')[1]), int(x['date'].split('-')[2])))
            
            for item in sorted_anniversaries:
                name = item['name'].replace("&", r"\&")
                if whimsy:
                    style = WHIMSY_STYLES.get("Anniversary")
                    if style:
                        name = rf"\textcolor{{{style['color']}}}{{{style['icon']} {name}}}"
                
                # Format Date: M D, Y
                dt = datetime.datetime.strptime(item['date'], "%Y-%m-%d")
                date_str = dt.strftime("%b %-d, %Y")
                
                # Calculate Years
                anniversary = dt.date()
                years = today.year - anniversary.year - ((today.month, today.day) < (anniversary.month, anniversary.day))

                f.write(rf"{name} & {date_str} ({years}) \\" + "\n")

            f.write(r"\end{tabular}" + "\n")
            f.write(r"}" + "\n")
            f.write(r"\end{minipage}" + "\n")
            
            f.write(r"\hfill" + "\n")
            
            f.write(r"\begin{minipage}[t]{0.48\textwidth}" + "\n")
            f.write(r"\centering" + "\n")
            if toc_enabled:
                f.write(r"\textbf{Table of Contents} \par \vspace{2mm}" + "\n")
                f.write(r"\begin{tabular}{lr}" + "\n") # Use tabular for alignment
                f.write(r"Title Page & \pageref{sec:title} \\" + "\n")
                for m in range(1, 13):
                    m_name = calendar.month_name[m]
                    if is_test_content("MONTH_SUMMARY", month=m):
                        f.write(rf"{m_name} & \pageref{{sec:month_{m}}} \\" + "\n")
                    else:
                        f.write(rf"{m_name} & (Skipped) \\" + "\n")
                
                # Add Event Lists (Dynamic check)
                for i in range(1, 15): # Check up to 15 potential event lists
                    f.write(rf"\eventlistrow{{{i}}}" + "\n")

                if not test_mode:
                    f.write(r"Extra Pages & \pageref{sec:extra_pages} \\" + "\n")
                else:
                    f.write(r"Extra Pages & (Skipped) \\" + "\n")
                    
                if include_source:
                    f.write(r"Source Code & \pageref{sec:source} \\" + "\n")
                f.write(r"\end{tabular}" + "\n")
            f.write(r"\end{minipage}" + "\n")
            
            f.write(r"\vfill" + "\n")

            # Info Box at Bottom Right
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(r"\begin{tikzpicture}[remember picture, overlay]" + "\n")
            f.write(rf"  \node[anchor=south east, xshift=-{TARGET_MARGIN_OUTER}mm, yshift=1cm] at (current page.south east) {{" + "\n")
            f.write(r"    \begin{minipage}{10cm}" + "\n")
            f.write(r"      \flushright \small \ttfamily" + "\n")
            f.write(rf"      Start Year: {START_YEAR} \\" + "\n")
            f.write(rf"      Num Years: {NUM_YEARS} \\" + "\n")
            f.write(rf"      Lines/Day: {NUM_WRITING_LINES} \\" + "\n")
            f.write(rf"      Sundays Red: {SUNDAYS_RED} \\" + "\n")
            f.write(rf"      Paper: {CURRENT_PAPER_KEY.replace('_', r'\_')} \\" + "\n")
            f.write(rf"      Test Mode: {test_mode} \\" + "\n")
            f.write(rf"      Spread: {spread_mode} ({DAYS_PER_PAGE} day/page) \\" + "\n")
            f.write(rf"      Align: {align_mode} \\" + "\n")
            f.write(rf"      Generated: {now_str}" + "\n")
            f.write(r"    \end{minipage}" + "\n")
            f.write(r"  };" + "\n")
            f.write(r"\end{tikzpicture}" + "\n")

            f.write(r"\end{titlepage}" + "\n")
            physical_page_count += 1

        # We need a reference leap year to ensure we iterate through Feb 29.
        ref_year = START_YEAR
        while not calendar.isleap(ref_year):
            ref_year += 1

        page_num = 2  # Start on page 2 (Left) after title page

        def generate_month_summary(month, page_num):
            """Generates a 1-page summary for the month."""
            month_name = calendar.month_name[month]
            days_in_month = calendar.monthrange(ref_year, month)[1]
            
            # Layout Constants
            ROW_H = 8 # mm
            HEADER_H = 15 # mm
            
            # Calculate column widths
            # Day Num + 10 Years
            DAY_NUM_W = 8
            YEAR_COL_W = (CALC_TEXT_WIDTH - DAY_NUM_W) / NUM_YEARS
            
            if is_test_content("MONTH_SUMMARY", month=month):
                # Ensure we start on an Odd (Right) page
                if page_num % 2 == 0: # Even/Left
                    ensure_parity(page_num + 1) # Force skip to Odd
                    page_num += 1
                
                ensure_parity(page_num)
                f.write(rf"\setcounter{{page}}{{{page_num}}}" + "\n")
                f.write(rf"\label{{sec:month_{month}}}" + "\n")
                
                f.write(r"\begin{center}" + "\n")
                f.write(rf"{{\Large \textbf{{{month_name} Summary}}}}" + "\n")
                f.write(r"\end{center}" + "\n")
                
                f.write(r"\vspace{5mm}" + "\n")
                
                # TikZ Grid
                grid_h = (days_in_month + 1) * ROW_H
                
                f.write(rf"\begin{{tikzpicture}}[x=1mm, y=1mm]" + "\n")
                
                w = DAY_NUM_W + NUM_YEARS * YEAR_COL_W
                
                # Grid Boundaries for Day Cells
                grid_top = grid_h - ROW_H
                grid_bottom = 0
                grid_left = DAY_NUM_W
                grid_right = w

                # Draw Horizontal Lines (Only for Day rows)
                for d in range(1, days_in_month + 2):
                    y = grid_h - (d * ROW_H)
                    f.write(rf"\draw[bordergray] ({grid_left}, {y}) -- ({grid_right}, {y});" + "\n")
                    
                # Draw Vertical Lines (Only for Year columns)
                for i in range(NUM_YEARS + 1):
                    x = grid_left + (i * YEAR_COL_W)
                    f.write(rf"\draw[bordergray] ({x}, {grid_bottom}) -- ({x}, {grid_top});" + "\n")

                # --- CONTENT ---
                
                # 1. Day Numbers (Column 0)
                for day in range(1, days_in_month + 1):
                    y_center = grid_h - (day * ROW_H) - (ROW_H / 2)
                    f.write(rf"\node[anchor=center] at ({DAY_NUM_W/2}, {y_center}) {{\small \textbf{{{day}}}}};" + "\n")
                    
                # 2. Year Headers (Row 0)
                header_y = grid_h - (ROW_H / 2)
                for i in range(NUM_YEARS):
                    curr_year = START_YEAR + i
                    header_x = DAY_NUM_W + (i * YEAR_COL_W) + (YEAR_COL_W / 2)
                    f.write(rf"\node[anchor=center] at ({header_x}, {header_y}) {{\textbf{{{curr_year}}}}};" + "\n")
                    
                # 3. Day Cells
                for day in range(1, days_in_month + 1):
                    row_top_y = grid_h - (day * ROW_H)
                    for i in range(NUM_YEARS):
                        curr_year = START_YEAR + i
                        col_left_x = DAY_NUM_W + (i * YEAR_COL_W)
                        dow = get_day_of_week(curr_year, month, day)[:2]
                        color_cmd = r"\color{sundayred}" if dow == "Su" and SUNDAYS_RED else ""
                        f.write(rf"\node[anchor=north west, inner sep=1pt] at ({col_left_x + 1}, {row_top_y - 1}) {{\tiny {color_cmd} {dow}}};" + "\n")

                f.write(r"\end{tikzpicture}" + "\n")
                
                # Draw Edge Index
                draw_edge_index(month)
                
                f.write(r"\newpage" + "\n")
                nonlocal physical_page_count
                physical_page_count += 1
            
            return page_num + 1

        # Removed old render_event_list definition as it is now defined earlier


        # Iterate through months to ensure proper pagination (Start Month on Right/Odd Page)
        for month in range(1, 13):
            # Collect days for this month
            month_days = []
            days_in_month = calendar.monthrange(ref_year, month)[1]
            for day in range(1, days_in_month + 1):
                month_days.append((month, day))

            if not month_days:
                continue

            # --- MONTH SUMMARY (1 Page) ---
            # Logic inside generate_month_summary ensures it starts on Odd page
            page_num = generate_month_summary(month, page_num)

            # Iterate through days in chunks
            for i in range(0, len(month_days), DAYS_PER_PAGE):
                chunk = month_days[i:i + DAYS_PER_PAGE]
                
                # Check if we should generate this page
                is_chunk_test = False
                if not test_mode:
                    is_chunk_test = True
                else:
                    for _, d in chunk:
                        if is_test_content("DAILY", month=month, day=d):
                            is_chunk_test = True
                            break
                
                if not is_chunk_test:
                    page_num += 1
                    continue

                ensure_parity(page_num)
                f.write(rf"\setcounter{{page}}{{{page_num}}}" + "\n")

                # Check for Trailing Blank Column
                has_blank_col = (len(chunk) == 1 and DAYS_PER_PAGE == 2)

                for col_idx in range(DAYS_PER_PAGE):
                    # Separator between columns
                    if col_idx > 0:
                        f.write(r"\hfill" + "\n")

                    # Start Column Minipage
                    f.write(rf"\begin{{minipage}}[t]{{{COL_WIDTH}mm}}" + "\n")

                    # Determine Content for this Column
                    if col_idx < len(chunk):
                        # Render Daily Content
                        month, day = chunk[col_idx]
                        month_name = calendar.month_name[month].upper()

                        # Determine Alignment for this column
                        align_right = False

                        # Determine if this is an Inner or Outer column
                        # Even Page (Left): Col 0 = Outer, Col 1 = Inner
                        # Odd Page (Right): Col 0 = Inner, Col 1 = Outer
                        is_inner_col = False
                        if page_num % 2 == 0:  # Even
                            if col_idx == 1:
                                is_inner_col = True
                        else:  # Odd
                            if col_idx == 0:
                                is_inner_col = True

                        if align_mode == "mirrored":
                            if page_num % 2 != 0:  # Odd/Right Page
                                align_right = True
                            else:  # Even/Left Page
                                align_right = False
                        elif align_mode == "left":
                            align_right = False

                        # --- HEADER LOGIC ---
                        f.write(rf"\begin{{minipage}}[t][{HEADER_H}mm]{{\textwidth}}")

                        # Determine content parts
                        day_str = rf"\huge \textbf{{{day}}}"
                        month_str = rf"\huge \textbf{{{month_name}}}"

                        # Determine if we show month
                        show_month = True
                        if DAYS_PER_PAGE == 2 and is_inner_col:
                            # Generally hide month on inner columns to reduce clutter
                            show_month = False
                            # EXCEPTION: Always show month on the last day of the month
                            if day == days_in_month:
                                show_month = True

                        # Build the header line
                        if align_right:
                            # Labels on Right (Right Page)
                            f.write(r"\hfill ")
                            if show_month:
                                f.write(rf"{month_str} \quad ")
                            f.write(rf"\makebox[{YEAR_LABEL_WIDTH}mm][r]{{{day_str}}}")
                        else:
                            # Labels on Left (Left Page)
                            f.write(rf"\makebox[{YEAR_LABEL_WIDTH}mm][l]{{{day_str}}}")
                            if show_month:
                                f.write(rf" \quad {month_str}")
                            f.write(r" \hfill")

                        f.write(r"\end{minipage}")
                        f.write(r"\par \nointerlineskip")

                        # --- 10 YEAR BLOCKS ---
                        for y_idx in range(NUM_YEARS):
                            curr_year = START_YEAR + y_idx
                            weekday = get_day_of_week(curr_year, month, day)

                            is_leap_year = calendar.isleap(curr_year)
                            is_feb_29 = (month == 2 and day == 29)
                            skip_content = is_feb_29 and not is_leap_year

                            if not skip_content:
                                label_year = f"{curr_year}"
                                label_day = f"{weekday}"
                                
                                if kanji_enabled:
                                    kanji = KANJI_DAYS.get(weekday, "")
                                    if kanji:
                                        label_day += f" {kanji}"
                                    
                                    # Squish all days to prevent wrapping and ensure visual consistency
                                    label_day = rf"\scalebox{{0.85}}[1.0]{{{label_day}}}"

                                if SUNDAYS_RED and weekday == "Sun":
                                    day_color = "sundayred"
                                else:
                                    day_color = "textgray"

                            # --- DRAW THE BLOCK ---
                            f.write(rf"\begin{{tikzpicture}}[x=1mm, y=1mm, trim left=0mm, trim right={COL_WIDTH}mm]" + "\n")

                            w = COL_WIDTH
                            h = BLOCK_H

                            f.write(rf"\path[use as bounding box] (0,0) rectangle ({w}, {h});" + "\n")

                            line_spacing = h / NUM_WRITING_LINES
                            circle_radius = line_spacing * 0.25

                            if not skip_content:
                                # Align labels to match header alignment
                                if align_right:
                                    f.write(rf"\node[anchor=north east, text width={YEAR_LABEL_WIDTH}mm, align=right, inner sep=0pt, yshift={LABEL_Y_SHIFT}mm] at ({w},{h}) {{\textbf{{{label_year}}}\\ \small \color{{{day_color}}} {label_day}}};" + "\n")
                                else:
                                    f.write(rf"\node[anchor=north west, text width={YEAR_LABEL_WIDTH}mm, align=left, inner sep=0pt, yshift={LABEL_Y_SHIFT}mm] at (0,{h}) {{\textbf{{{label_year}}}\\ \small \color{{{day_color}}} {label_day}}};" + "\n")

                            # Top Border (First block only)
                            if y_idx == 0:
                                f.write(rf"\draw[bordergray] (0, {h}) -- ({w}, {h});" + "\n")

                            # Guide Lines
                            if not skip_content:
                                guide_gap = YEAR_LABEL_WIDTH + 1

                                # Special Events Injection
                                events = get_special_events(curr_year, month, day, use_whimsy=whimsy)
                                if events:
                                    event_str = ", ".join(events)
                                    event_str = event_str.replace("&", r"\&")
                                    y_text = h - 0.5 * line_spacing
                                    if align_right:
                                        # Text on Left (Inner edge)
                                        # Circle is at cx = circle_radius + 1
                                        # Text should start after circle
                                        x_text = (circle_radius + 1) + circle_radius + 1
                                        f.write(rf"\node[anchor=west, inner sep=0, text=textgray, font=\footnotesize] at ({x_text}, {y_text}) {{{event_str}}};" + "\n")
                                    else:
                                        # Text on Right (after label)
                                        f.write(rf"\node[anchor=west, inner sep=0, text=textgray, font=\footnotesize] at ({guide_gap} + 1, {y_text}) {{{event_str}}};" + "\n")

                                # Circles for first two lines (Inside end)
                                for s in range(2):  # First two spaces
                                    y_circle = h - (s + 0.5) * line_spacing
                                    if align_right:  # Inner is Left
                                        cx = circle_radius + 1
                                    else:  # Inner is Right
                                        cx = w - circle_radius - 1
                                    f.write(rf"\draw[guidegray] ({cx}, {y_circle}) circle ({circle_radius});" + "\n")

                                # Continuation 'p' prompt
                                # Anchor to bottom writing guide (y=0) to avoid touching top guide
                                f.write(rf"\node[anchor=south east, inner sep=0, text=textgray, yshift=0.5mm] at ({w}-6, 0) {{\small $\vec{{p}}$}};" + "\n")

                                for l in range(1, NUM_WRITING_LINES):
                                    y_pos = h - l * line_spacing
                                    if l == 1:
                                        # Shortened Guide Line
                                        if align_right:
                                            f.write(rf"\draw[guidegray, dash pattern=on 0.5pt off 1pt] (0, {y_pos}) -- ({w} - {guide_gap}, {y_pos});" + "\n")
                                        else:
                                            f.write(rf"\draw[guidegray, dash pattern=on 0.5pt off 1pt] ({guide_gap}, {y_pos}) -- ({w}, {y_pos});" + "\n")
                                    else:
                                        f.write(rf"\draw[guidegray, dash pattern=on 0.5pt off 1pt] (0, {y_pos}) -- ({w}, {y_pos});" + "\n")

                            # Bottom Divider
                            f.write(rf"\draw[bordergray] (0, 0) -- ({w}, 0);" + "\n")

                            f.write(r"\end{tikzpicture}" + "\n")
                            f.write(r"\par \nointerlineskip" + "\n")
                    
                    elif has_blank_col:
                        # Render Event List in the blank column -> CHANGED: Leave blank
                        f.write(r"\hfill" + "\n")

                    # End Column Minipage
                    f.write(r"\end{minipage}" + "\n")

                # Draw Edge Index
                draw_edge_index(month)

                # End of Page Chunk
                f.write(r"\newpage" + "\n")
                physical_page_count += 1
                page_num += 1

        # --- EVENT LISTS APPENDIX ---
        if event_lists_enabled:
            # Ensure we start on an Odd (Right) page
            if page_num % 2 == 0: # Even/Left
                ensure_parity(page_num + 1) # Force skip to Odd
                page_num += 1
            
            ensure_parity(page_num)
            
            # Generate 6 Event Lists
            for i in range(6):
                # Render Full Page Event List
                render_event_list(event_list_counter, width=CALC_TEXT_WIDTH)
                event_list_counter += 1
                f.write(r"\newpage" + "\n")
                physical_page_count += 1
                page_num += 1

        # --- EXTRA PAGES ---
        # 10 pages (5 sheets) of lined notes
        # We ensure the Source Code starts on an Odd page (Right side / Fresh sheet).
        # If after 10 pages, the next page is Even, we add one more extra page.
        MIN_EXTRA_PAGES = 10
        
        # Ensure we start on an Odd (Right) page
        if page_num % 2 == 0: # Even/Left
            ensure_parity(page_num + 1) # Force skip to Odd
            page_num += 1
        
        ensure_parity(page_num)

        # Calculate how many pages we need
        # Current page_num is the start of extra pages.
        # If (page_num + 10) is Even, next page is Even. We want Odd. So we need 11.
        # If (page_num + 10) is Odd, next page is Odd. Good. We need 10.
        if (page_num + MIN_EXTRA_PAGES) % 2 == 0:
            num_extra_pages = MIN_EXTRA_PAGES + 1
        else:
            num_extra_pages = MIN_EXTRA_PAGES

        # Calculate lines for full page
        line_spacing = BLOCK_H / NUM_WRITING_LINES

        # Usable height for extra pages
        # Reduce height by one line to make room for "date" annotation
        EXTRA_USABLE_H = USABLE_H - line_spacing

        # Calculate column width for 2 columns
        EXTRA_COL_WIDTH = (CALC_TEXT_WIDTH - COLUMN_GUTTER) / 2

        num_lines_extra = int(EXTRA_USABLE_H / line_spacing)

        for i in range(num_extra_pages):
            if is_test_content("EXTRA_PAGES", page_idx=i):
                ensure_parity(page_num)
                f.write(rf"\setcounter{{page}}{{{page_num}}}" + "\n")
                
                if i == 0:
                    f.write(r"\label{sec:extra_pages}" + "\n")

                # --- HEADER ---
                f.write(rf"\begin{{minipage}}[t][{HEADER_H}mm]{{\textwidth}}")
                
                header_text = r"\huge \textbf{Extra Pages}"
                
                # Align based on page parity (Mirrored)
                # Even (Left): Align Left
                # Odd (Right): Align Right
                if page_num % 2 == 0: # Even/Left
                     f.write(rf"\makebox[\textwidth][l]{{{header_text}}}")
                else: # Odd/Right
                     f.write(rf"\makebox[\textwidth][r]{{{header_text}}}")

                f.write(r"\end{minipage}")
                f.write(r"\par \nointerlineskip")
                
                # Add spacing so "date" annotation doesn't overlap header
                f.write(rf"\vspace{{{line_spacing}mm}}" + "\n")

                # --- COLUMNS ---
                for col in range(2):
                    if col > 0:
                        f.write(r"\hfill" + "\n")
                        
                    f.write(rf"\begin{{minipage}}[t]{{{EXTRA_COL_WIDTH}mm}}" + "\n")
                    
                    # TikZ for lines
                    f.write(rf"\begin{{tikzpicture}}[x=1mm, y=1mm]" + "\n")
                    f.write(rf"\path[use as bounding box] (0,0) rectangle ({EXTRA_COL_WIDTH}, {EXTRA_USABLE_H});" + "\n")
                    
                    # "date" annotation
                    # Top left of the column, above the writing area.
                    f.write(rf"\node[anchor=south west, inner sep=0, text=textgray, yshift=0.5mm] at (0, {EXTRA_USABLE_H}) {{\small \textit{{date}}}};" + "\n")
                    
                    # Lines
                    # Top Border
                    f.write(rf"\draw[bordergray] (0, {EXTRA_USABLE_H}) -- ({EXTRA_COL_WIDTH}, {EXTRA_USABLE_H});" + "\n")
                    
                    for l in range(1, num_lines_extra + 1):
                        y_pos = EXTRA_USABLE_H - l * line_spacing
                        # Bottom border for the last line
                        if l == num_lines_extra:
                             f.write(rf"\draw[bordergray] (0, {y_pos}) -- ({EXTRA_COL_WIDTH}, {y_pos});" + "\n")
                        else:
                             f.write(rf"\draw[guidegray, dash pattern=on 0.5pt off 1pt] (0, {y_pos}) -- ({EXTRA_COL_WIDTH}, {y_pos});" + "\n")

                    f.write(r"\end{tikzpicture}" + "\n")
                    f.write(r"\end{minipage}" + "\n")

                f.write(r"\newpage" + "\n")
                physical_page_count += 1

            page_num += 1

        # --- SOURCE CODE APPENDIX ---
        # Self-preservation: Print the source code of this script at the end of the journal.
        if include_source and is_test_content("SOURCE"):
            # Ensure we start on an Odd (Right) page
            if page_num % 2 == 0: # Even/Left
                ensure_parity(page_num + 1) # Force skip to Odd
                page_num += 1
            
            ensure_parity(page_num)
            # Ensure the page number is correct (continuing from the last logical page)
            f.write(rf"\setcounter{{page}}{{{page_num}}}" + "\n")
            
            # Reset geometry to maximize space for code (this forces a new page)
            # Respect inner margin for binding/hole punches
            f.write(rf"\newgeometry{{top=10mm, bottom=10mm, inner={TARGET_MARGIN_INNER}mm, outer=10mm}}" + "\n")
            
            # Landscape mode for source code
            f.write(r"\begin{landscape}" + "\n")
            f.write(r"\section*{Source Code: forever\_journal.py}" + "\n")
            f.write(r"\label{sec:source}" + "\n")
            
            # Configure listings
            f.write(r"\lstset{" + "\n")
            f.write(r"  language=Python," + "\n")
            f.write(r"  basicstyle=\tiny\ttfamily," + "\n")
            f.write(r"  keywordstyle=\color{blue}," + "\n")
            f.write(r"  stringstyle=\color{codepurple}," + "\n")
            f.write(r"  commentstyle=\color{codegreen}," + "\n")
            f.write(r"  breaklines=true," + "\n")
            f.write(r"  showstringspaces=false," + "\n")
            f.write(r"  numbers=none," + "\n")
            f.write(r"  frame=single," + "\n")
            f.write(r"  rulecolor=\color{lightgray}" + "\n")
            f.write(r"}" + "\n")
            
            # 3 Columns
            f.write(r"\begin{multicols}{3}" + "\n")
            f.write(r"\begin{lstlisting}" + "\n")
            
            # Read and write the source code of this file
            # We must be careful not to print the end-listing tag literally, or it will break the LaTeX.
            try:
                with open(os.path.abspath(__file__), "r") as source_file:
                    for line in source_file:
                        f.write(line)
            except Exception as e:
                f.write(f"# Error reading source code: {e}")
            
            # Safe way to write the end tag without breaking the listing
            f.write(r"\end{lst" + "listing}" + "\n")
            f.write(r"\end{multicols}" + "\n")
            f.write(r"\end{landscape}" + "\n")
            
        f.write(r"\end{CJK*}" + "\n")
        f.write(r"\end{document}")

    print(f"Generated: {output_tex}")
    print(f"Configuration: Paper={CURRENT_PAPER_KEY} ({PAGE_W}x{PAGE_H}mm)")
    print(f"Margins: Inner={TARGET_MARGIN_INNER}mm, Outer={TARGET_MARGIN_OUTER}mm, Top={TARGET_MARGIN_TOP}mm, Bottom={TARGET_MARGIN_BOTTOM}mm")
    print(f"Layout: {spread_mode} ({DAYS_PER_PAGE} days/page), Align: {align_mode}")

    # --- AUTO-COMPILE LOGIC ---
    if not no_compile:
        pdflatex_path = shutil.which("pdflatex")
        if pdflatex_path:
            print(f"Found pdflatex at: {pdflatex_path}")
            print("Compiling PDF...")
            try:
                # Run pdflatex with output directory
                # Note: We pass the full path to the tex file.
                # pdflatex will write aux/log/pdf to the directory specified by -output-directory
                cmd = [
                    pdflatex_path,
                    f"-output-directory={OUTPUT_DIR}",
                    "-interaction=nonstopmode", # Don't hang on errors
                    output_tex
                ]
                
                if single_pass:
                    print("Compiling (Single Pass)...")
                    print("Warning: ToC and Edge Index may be incorrect due to missing second pass.")
                    subprocess.run(cmd, check=True)
                else:
                    # Always run twice.
                    # 1. ToC references (if enabled)
                    # 2. TikZ [remember picture, overlay] for Edge Indexing (always enabled)
                    print("Pass 1/2...")
                    subprocess.run(cmd, check=True)
                    
                    print("Pass 2/2 (Resolving references & overlays)...")
                    subprocess.run(cmd, check=True)
                
                print(f"Success! PDF generated at: {os.path.join(OUTPUT_DIR, output_base + '.pdf')}")
            except subprocess.CalledProcessError as e:
                print("Error during PDF compilation.")
                print(e)
        else:
            print("\n[NOTICE] pdflatex not found in PATH.")
            print("To generate the PDF, please install a LaTeX distribution (e.g., TeX Live, MacTeX).")
            print(f"Then run: pdflatex -output-directory {OUTPUT_DIR} {output_tex}")
    else:
        print(f"Skipping compilation. To compile manually: pdflatex -output-directory {OUTPUT_DIR} {output_tex}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Forever Journal LaTeX")
    parser.add_argument("--test", action="store_true", help="Generate a test PDF with specific leap year spreads")
    parser.add_argument("--spread", choices=["2up", "4up"], default="2up", help="2up = 1 day/page, 4up = 2 days/page")
    parser.add_argument("--align", choices=["mirrored", "left"], default="mirrored", help="mirrored = Outer aligned, left = Left aligned")
    parser.add_argument("--no-compile", action="store_true", help="Skip automatic PDF compilation")
    parser.add_argument("--include-source", action="store_true", help="Append source code to the PDF")
    parser.add_argument("--toc", action="store_true", help="Include Table of Contents (requires 2-pass compilation)")
    parser.add_argument("--whimsy", action="store_true", help="Add icons and colors to special days")
    parser.add_argument("--single-pass", action="store_true", help="Run pdflatex only once (faster, but ToC/Edge Index may be broken)")
    parser.add_argument("--event-lists", action="store_true", help="Enable Event List filler pages")
    parser.add_argument("--kanji", action="store_true", help="Add Japanese Kanji to day labels")
    parser.add_argument("--num-years", type=int, default=10, help="Number of years to track (default: 10)")
    parser.add_argument("--num-lines", type=int, default=5, help="Number of writing lines per block (default: 5)")
    args = parser.parse_args()

    generate_tex(test_mode=args.test, spread_mode=args.spread, align_mode=args.align, no_compile=args.no_compile, include_source=args.include_source, toc_enabled=args.toc, whimsy=args.whimsy, single_pass=args.single_pass, event_lists_enabled=args.event_lists, kanji_enabled=args.kanji, num_years=args.num_years, num_writing_lines=args.num_lines)
