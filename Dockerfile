# Use official lightweight Python image
FROM python:3.11-slim-bookworm

# Install TeX Live and dependencies
# 1. Update package lists
# 2. Install minimal texlive + recommended packages (includes fonts, latex, etc)
# 3. Install build-essential for any python extensions if needed (rare for this stack)
# 4. Clean up to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-xetex \
    texlive-lang-cjk \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code (we will likely mount volume in practice, but this is good for archival)
COPY . .

# Default command: show help
ENTRYPOINT ["python", "run.py"]
CMD ["--help"]
