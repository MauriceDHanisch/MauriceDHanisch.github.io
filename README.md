# Website Scripts Guide

This repository contains several Python scripts to automate content updates and optimization.

## Requirements

Install the dependencies:
```bash
pip install -r scripts/requirements.txt
```

## Scripts

### 1. Update Publications (`scripts/update_pubs.py`)
Fetches your latest publications from Google Scholar, formats them, and updates the website.

**Usage:**
```bash
python3 scripts/update_pubs.py
```
**What it does:**
- Scrapes Google Scholar for your profile.
- Fills in missing details (authors, venue).
- Formats names (e.g., "M. Hanisch").
- Generates HTML with the new design (badges, buttons).
- Updates `content/publications.html` and `content/selected_publications.html`.

### 2. Sync CV (`scripts/sync_cv.py`)
Updates the public CV PDF from your private CV repository.

**Usage:**
```bash
python3 scripts/sync_cv.py
```
**What it does:**
- Checks for your private CV repo at `assets/cv_repo`.
- Copies the latest PDF to `assets/pdf/Maurice_Hanisch_CV.pdf`.
- **Note:** You must clone your private repo to `assets/cv_repo` first.

### 3. Optimize Assets (`scripts/optimize.py`)
Optimizes images and minifies CSS/JS for better performance.

**Usage:**
```bash
python3 scripts/optimize.py
```
**What it does:**
- Converts images in `assets/img` to WebP.
- Resizes large images.
- Minifies `style.css` -> `style.min.css`.
- Minifies `main.js` -> `main.min.js`.