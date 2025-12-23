import os

OUTPUT_TEX = "margin_test.tex"

# Paper Sizes (mm)
PAPER_SIZES = {
    "US_LETTER": {"w": 215.9, "h": 279.4, "name": "US Letter", "latex_opt": "letterpaper"},
    "A4":        {"w": 210.0, "h": 297.0, "name": "A4",        "latex_opt": "a4paper"}
}

# Select Paper Size
CURRENT_PAPER_KEY = "A4"
PAPER = PAPER_SIZES[CURRENT_PAPER_KEY]

# Offsets in mm (Adjustable variables)
OFFSET_TOP_FRONT_MM = 1.8
OFFSET_LEFT_FRONT_MM = 2.0

OFFSET_TOP_BACK_MM = 1.8
OFFSET_LEFT_BACK_MM = 2.5

def get_tikz_grid(offset_top, offset_left, side_label):
    # Convert mm to cm for TikZ
    page_w_cm = PAPER["w"] / 10
    page_h_cm = PAPER["h"] / 10
    
    return rf"""
\begin{{tikzpicture}}[remember picture, overlay, shift={{(current page.north west)}}, shift={{({offset_left/10}, -{offset_top/10})}}]

    % Paper Dimensions in cm
    \def\pagewidth{{{page_w_cm}}}
    \def\pageheight{{{page_h_cm}}}

    % 1. Minor Grid (1mm)
    \draw[step=0.1cm, gray!20, very thin] (0,0) grid (\pagewidth, -\pageheight);

    % 2. Medium Grid (0.5cm)
    \draw[step=0.5cm, gray!40, thin] (0,0) grid (\pagewidth, -\pageheight);

    % 3. Major Grid (1cm)
    \draw[step=1cm, gray!70, thick] (0,0) grid (\pagewidth, -\pageheight);

    % 3. Labels and Markers
    % X-axis
    \foreach \x in {{0,1,...,{int(page_w_cm)}}} {{
        \node[font=\small, red] at (\x + 0.5, -0.5) {{\x}};
        \draw[->, red, thick] (\x + 0.25, -0.25) -- (\x + 0.05, -0.05);
        \draw[red, thick] (\x, 0) -- (\x, -0.5);
    }}

    % Y-axis
    \foreach \y in {{1,2,...,{int(page_h_cm)}}} {{
        \node[font=\small, red] at (0.5, -\y - 0.5) {{\y}};
        \draw[->, red, thick] (0.25, -\y - 0.25) -- (0.05, -\y - 0.05);
        \draw[red, thick] (0, -\y) -- (0.5, -\y);
    }}

    % 4. Edge Warning Lines
    \draw[red, thick] (0,0) rectangle (\pagewidth, -\pageheight);

    % 5. Center Info
    \node[anchor=center] at (\pagewidth/2, -\pageheight/2) {{\Huge \textbf{{Printer Margin Test - {side_label}}}}};
    \node[anchor=center] at (\pagewidth/2, -\pageheight/2 - 1) {{\Large {PAPER['name']} ({PAPER['w']}mm x {PAPER['h']}mm)}};
    \node[anchor=center] at (\pagewidth/2, -\pageheight/2 - 2) {{Grid Origin (0,0) is Top-Left Corner}};
    \node[anchor=center] at (\pagewidth/2, -\pageheight/2 - 3) {{Major: 1cm | Medium: 0.5cm | Minor: 1mm}};
    \node[anchor=center, red] at (\pagewidth/2, -\pageheight/2 - 4) {{Offsets Applied: Top {offset_top}mm, Left {offset_left}mm}};

\end{{tikzpicture}}
"""

def generate_margin_test():
    with open(OUTPUT_TEX, "w") as f:
        f.write(rf"""\documentclass{{article}}
\usepackage[paperwidth={PAPER['w']}mm, paperheight={PAPER['h']}mm, margin=0pt]{{geometry}}
\usepackage{{tikz}}
\usepackage{{helvet}}
\renewcommand{{\familydefault}}{{\sfdefault}}

\pagestyle{{empty}}
\setlength{{\parindent}}{{0pt}}

\begin{{document}}
""")
        # Page 1: Front
        f.write(r"\mbox{}" + "\n") # Invisible content to ensure page creation
        f.write(get_tikz_grid(OFFSET_TOP_FRONT_MM, OFFSET_LEFT_FRONT_MM, "FRONT SIDE"))
        f.write(r"\clearpage" + "\n")
        
        # Page 2: Back
        f.write(r"\mbox{}" + "\n") # Invisible content to ensure page creation
        f.write(get_tikz_grid(OFFSET_TOP_BACK_MM, OFFSET_LEFT_BACK_MM, "BACK SIDE"))
        
        f.write(r"\end{document}")

    print(f"Generated {OUTPUT_TEX}")

if __name__ == "__main__":
    generate_margin_test()
