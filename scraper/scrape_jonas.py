#!/usr/bin/env python3
"""
scrape_jonas.py
───────────────
Scrapes manuscript metadata from the Jonas catalog (IRHT-CNRS).
Outputs docs/data/manuscripts.json relative to the repository root.

Usage:
  python scraper/scrape_jonas.py

To add more manuscripts:
  Find a manuscript on https://jonas.irht.cnrs.fr/
  Note the number after 'projet=' in the URL (e.g. ?projet=71291)
  Add that number to the MANUSCRIPT_IDS list below.
"""

import json
import time
import re
import sys
import requests
from bs4 import BeautifulSoup
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION — edit these to add manuscripts
# ──────────────────────────────────────────────────────────────────────────────

BASE_URL = "https://jonas.irht.cnrs.fr/consulter/manuscrit/detail_manuscrit.php?projet={}"

# Jonas project IDs for manuscripts to include.
# Find IDs by browsing Jonas: https://jonas.irht.cnrs.fr/
MANUSCRIPT_IDS = [
    71291,   # Paris, BnF, fr. 23112 (XIIIe s., 62 texts, Picardie)
    # Add more IDs here, one per line:
    # 12345,
    # 67890,
]

# Keywords used to identify which saints' Lives appear in each manuscript.
# Keys must match the saint page filenames in docs/saints/ (without .html).
# Values are lists of substrings to search for in work titles (case-insensitive).
SAINT_KEYWORDS = {
    "saint-martin":    ["martin"],
    "saint-catherine": ["catherine", "katherina"],
    "saint-nicholas":  ["nicolas", "nicholas", "nicolai"],
    "saint-margaret":  ["marguerite", "margaret", "margareta"],
}

# Where to write the output JSON
OUTPUT_PATH = Path(__file__).parent.parent / "docs" / "data" / "manuscripts.json"

# HTTP headers — identify the bot politely
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "research-scraper/1.0 hagiography-project "
        "(contact: your-email@example.com)"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}

# Seconds to wait between requests (be polite to Jonas servers)
DELAY_SECONDS = 2.5


# ──────────────────────────────────────────────────────────────────────────────
# PARSING HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def get_field(soup: BeautifulSoup, label: str) -> str:
    """
    Search for 'label' in <dt> or <th> elements and return the adjacent value.
    Uses <dd> (for dt) or the next <td> (for th) as the value container.
    Falls back to searching in any element whose text matches, then grabbing
    the next sibling's text.
    Returns empty string if not found.
    """
    label_lower = label.lower()

    # Strategy 1: dt/dd structure
    for dt in soup.find_all("dt"):
        if label_lower in dt.get_text(strip=True).lower():
            dd = dt.find_next_sibling("dd")
            if dd:
                return dd.get_text(separator=" ", strip=True)

    # Strategy 2: table th/td structure
    for th in soup.find_all("th"):
        if label_lower in th.get_text(strip=True).lower():
            td = th.find_next_sibling("td")
            if td:
                return td.get_text(separator=" ", strip=True)

    # Strategy 3: td/td (some Jonas tables use td for both label and value)
    for td in soup.find_all("td"):
        text = td.get_text(strip=True)
        if label_lower in text.lower() and len(text) < 80:
            sibling = td.find_next_sibling("td")
            if sibling:
                val = sibling.get_text(separator=" ", strip=True)
                if val:
                    return val

    return ""


def parse_shelfmark(soup: BeautifulSoup) -> str:
    """Extract the manuscript's full shelfmark from the first <h1>."""
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(separator=" ", strip=True)
    # Fallback: try <title>
    title = soup.find("title")
    if title:
        return title.get_text(strip=True)
    return ""


def clean_title(raw_title: str) -> dict:
    """
    Jonas work titles are formatted as: 'Author|Title|Incipit référence de l'oeuvre: ...'
    Split and return the meaningful parts.
    """
    parts = [p.strip() for p in raw_title.split("|")]
    # Remove the "Incipit référence" part (always the last segment if present)
    parts = [p for p in parts if not p.startswith("Incipit référence")]
    if len(parts) == 1:
        return {"author": "", "title": parts[0]}
    elif len(parts) >= 2:
        return {"author": parts[0], "title": parts[1]}
    return {"author": "", "title": raw_title}


def parse_contents(soup: BeautifulSoup) -> list:
    """
    Parse the Contenu (Contents) section.
    Jonas lists each work in a <div class='temoin'> containing an <a> link
    pointing to /consulter/oeuvre/detail_oeuvre.php?oeuvre=...
    Returns a list of work dicts.
    """
    contents = []
    seen_ids = set()

    # Work entries live in divs with class "temoin"
    # Link href matches detail_oeuvre.php (not recherche_oeuvre.php)
    work_links = soup.find_all(
        "a",
        href=re.compile(r"/consulter/oeuvre/detail_oeuvre\.php")
    )

    for link in work_links:
        href = link.get("href", "")
        if not href:
            continue

        # Resolve relative URL (Jonas uses ../../ prefixes)
        if href.startswith("../../"):
            href = href[5:]  # remove one level → /consulter/...
        elif href.startswith(".."):
            href = href.lstrip(".")

        # Deduplicate by oeuvre ID
        oeuvre_id_match = re.search(r"oeuvre=(\d+)", href)
        if not oeuvre_id_match:
            continue
        oeuvre_id = oeuvre_id_match.group(1)
        if oeuvre_id in seen_ids:
            continue
        seen_ids.add(oeuvre_id)

        raw_title = link.get_text(strip=True)
        title_parts = clean_title(raw_title)

        work = {
            "author":           title_parts["author"],
            "title":            title_parts["title"],
            "raw_title":        raw_title,
            "jonas_oeuvre_url": "https://jonas.irht.cnrs.fr/consulter/oeuvre/detail_oeuvre.php?oeuvre=" + oeuvre_id,
            "folio":            "",
            "date":             "",
            "incipit":          "",
            "explicit":         "",
        }

        # The container div has class "temoin" and contains td pairs for metadata
        container = link.parent
        for _ in range(6):
            if container is None:
                break
            if container.name == "div" and "temoin" in (container.get("class") or []):
                break
            container = container.parent

        if container:
            container_text = container.get_text(" ", strip=True)

            # Extract folio range: look for td pairs within the container
            for td in container.find_all("td"):
                td_text = td.get_text(strip=True).lower()
                next_td = td.find_next_sibling("td")
                if not next_td:
                    continue
                next_val = next_td.get_text(separator=" ", strip=True)

                if "folio" in td_text and len(td_text) < 40:
                    work["folio"] = next_val[:100]
                elif "datation" in td_text or ("date" in td_text and "tation" in td_text):
                    work["date"] = next_val[:100]
                elif td_text.startswith("incipit") and len(td_text) < 50:
                    work["incipit"] = next_val[:400]
                elif td_text.startswith("explicit") and len(td_text) < 50:
                    work["explicit"] = next_val[:400]

            # Fallback: regex for folio patterns in full container text
            if not work["folio"]:
                folio_match = re.search(
                    r"f(?:f)?\.?\s*(\d+\s*[rv]?[ab]?)\s*[-–—]\s*(?:f(?:f)?\.?\s*)?(\d+\s*[rv]?[ab]?)",
                    container_text,
                    re.IGNORECASE,
                )
                if folio_match:
                    work["folio"] = folio_match.group(0).strip()

        contents.append(work)

    return contents


def identify_saints(contents: list, saint_keywords: dict) -> list:
    """
    Return list of saint IDs whose keywords appear in any work title.
    """
    found = []
    for work in contents:
        title_lower = work["title"].lower()
        for saint_id, keywords in saint_keywords.items():
            if saint_id not in found:
                for kw in keywords:
                    if kw.lower() in title_lower:
                        found.append(saint_id)
                        break
    return found


# ──────────────────────────────────────────────────────────────────────────────
# MAIN SCRAPING FUNCTION
# ──────────────────────────────────────────────────────────────────────────────

def scrape_manuscript(project_id: int):
    """
    Fetch and parse one manuscript record from Jonas.
    Returns a dict of metadata, or None on failure.
    """
    url = BASE_URL.format(project_id)
    print(f"  → Fetching {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        resp.encoding = "utf-8"
    except requests.exceptions.HTTPError as e:
        print(f"    ✗ HTTP error for ID {project_id}: {e}", file=sys.stderr)
        return None
    except requests.exceptions.RequestException as e:
        print(f"    ✗ Network error for ID {project_id}: {e}", file=sys.stderr)
        return None

    soup = BeautifulSoup(resp.text, "lxml")

    # ── Core metadata ────────────────────────────────────────────────────────
    shelfmark = parse_shelfmark(soup)

    # Date field — Jonas uses "Datation détaillée" or just "Datation"
    date_str = (
        get_field(soup, "Datation détaillée")
        or get_field(soup, "Datation")
        or get_field(soup, "Date")
    )

    # Language
    language = (
        get_field(soup, "Langue principale")
        or get_field(soup, "Langue")
    )

    # Support material
    support = (
        get_field(soup, "Type support")
        or get_field(soup, "Support")
    )

    # Physical dimensions
    height_mm = get_field(soup, "Hauteur page")
    width_mm  = get_field(soup, "Largeur page")
    if height_mm and width_mm:
        # Extract just the numeric part if there are trailing labels
        h = re.search(r"\d+", height_mm)
        w = re.search(r"\d+", width_mm)
        dimensions = f"{h.group(0)} × {w.group(0)} mm" if h and w else ""
    else:
        dimensions = ""

    # Folios, columns, script, origin
    folios  = get_field(soup, "Nombre de feuillets")
    columns = get_field(soup, "Nombre de colonnes")
    script  = get_field(soup, "Type d'écriture") or get_field(soup, "Écriture")
    # "Origine géographique" is a section header; the actual value is under
    # "Localisation par la langue" (sub-label) → next sibling td = e.g. "Picardie"
    origin  = (
        get_field(soup, "Localisation par la langue")
        or get_field(soup, "Localisation")
        or get_field(soup, "Origine géographique")
    )

    # Provenance (ownership history, separate from geographic origin)
    provenance = get_field(soup, "Possesseur") or get_field(soup, "Provenance ancienne")

    # ── Contents ─────────────────────────────────────────────────────────────
    contents = parse_contents(soup)
    saints   = identify_saints(contents, SAINT_KEYWORDS)

    # ── Short date (century only, e.g. "13e s") ──────────────────────────────
    date_short_match = re.match(r"(\d+e\s*s\.?)", date_str)
    date_short = date_short_match.group(1) if date_short_match else date_str[:12]

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"    ✓ {shelfmark or '(no shelfmark)'}")
    print(f"      Date: {date_str or '—'}  |  Support: {support or '—'}  |"
          f"  Origin: {origin or '—'}")
    print(f"      Works found: {len(contents)}  |  Saints identified: {saints}")

    return {
        "jonas_id":          project_id,
        "jonas_url":         url,
        "shelfmark":         shelfmark,
        "date":              date_str,
        "date_short":        date_short,
        "language":          language,
        "support":           support,
        "dimensions":        dimensions,
        "folios":            folios,
        "columns":           columns,
        "script":            script,
        "origin":            origin,
        "provenance":        provenance,
        "saints":            saints,
        "contents":          contents,
        # Fill in the path to the transcription HTML once it exists:
        "transcription_file": "",
    }


# ──────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

def main():
    print(f"Scraping {len(MANUSCRIPT_IDS)} manuscript(s) from Jonas IRHT-CNRS...")
    print(f"Output: {OUTPUT_PATH}\n")

    results = []
    for i, ms_id in enumerate(MANUSCRIPT_IDS):
        ms = scrape_manuscript(ms_id)
        if ms:
            results.append(ms)
        # Polite delay between requests (skip after last item)
        if i < len(MANUSCRIPT_IDS) - 1:
            time.sleep(DELAY_SECONDS)

    # Write JSON
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nDone. Wrote {len(results)} record(s) to {OUTPUT_PATH}")
    if len(results) < len(MANUSCRIPT_IDS):
        failed = len(MANUSCRIPT_IDS) - len(results)
        print(f"WARNING: {failed} manuscript(s) failed to scrape.", file=sys.stderr)


if __name__ == "__main__":
    main()
