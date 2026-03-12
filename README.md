# Lives of the Saints — Medieval French Hagiographic Manuscripts

Research website for digital editions of saints' Lives from medieval manuscripts
in Old and Middle French (langue d'oïl).

---

## Project structure

```
vies-des-saints/
├── .github/workflows/scrape-jonas.yml   ← Automation (GitHub Actions)
├── docs/                                ← Website (served by GitHub Pages)
│   ├── index.html                       ← Homepage (3 panels: Lives / Saints / Manuscripts)
│   ├── saints.html                      ← Browse-by-saint grid (former homepage)
│   ├── lives.html                       ← Table of contents for all Lives (placeholder)
│   ├── manuscripts.html                 ← Manuscript index (Jonas data)
│   ├── search.html                      ← Site search (placeholder)
│   ├── about.html                       ← About the project
│   ├── css/style.css                    ← Styles (medieval design system)
│   ├── fonts/                           ← Junicode font (must be added manually)
│   ├── images/                          ← Saint and panel images (SVG placeholders)
│   ├── js/manuscripts-table.js          ← Sortable/filterable table
│   ├── js/nav.js                        ← Dropdown navigation logic
│   ├── saints/                          ← Individual saint pages
│   ├── transcriptions/                  ← Digital transcriptions
│   └── data/manuscripts.json           ← Data scraped from Jonas (auto-generated)
└── scraper/
    ├── scrape_jonas.py                  ← Scraping script
    └── requirements.txt
```

---

## Setup — Step-by-step guide for beginners

### Step 1: Create a GitHub account (if you don't have one)

1. Go to [github.com](https://github.com) and click **Sign up**
2. Fill in the form and confirm your email address
3. Choose the **Free** plan

---

### Step 2: Create a new repository

1. On your GitHub page, click the green **New** button (or go to github.com/new)
2. **Repository name**: choose a name, e.g. `vies-des-saints`
3. **Visibility**: choose **Public** (required for free GitHub Pages)
4. Check **Add a README file**
5. Click **Create repository**

---

### Step 3: Install GitHub Desktop

GitHub Desktop is a free application that lets you manage your repository
without using the command line.

1. Download it from [desktop.github.com](https://desktop.github.com)
2. Install it and sign in with your GitHub account
3. Click **Clone a repository from the Internet...**
4. Choose your `vies-des-saints` repository and select a folder on your computer
5. Click **Clone**

---

### Step 4: Copy the project files

1. Open the folder where you cloned the repository
2. Copy all files and folders from this project into that folder:
   - `.github/` (hidden folder — make sure it is included)
   - `docs/`
   - `scraper/`
   - `README.md`
3. In GitHub Desktop, you will see all these files listed under **Changes**
4. Type a message in the **Summary** field, e.g.: `Initial commit`
5. Click **Commit to main**
6. Click **Push origin** to send the files to GitHub

---

### Step 5: Configure GitHub Pages

1. On GitHub, open your repository and click the **Settings** ⚙ tab
2. In the left sidebar, click **Pages**
3. Under **Source**, choose **Deploy from a branch**
4. Under **Branch**, select **main** and the folder **/ (docs)**
5. Click **Save**
6. Wait 1–2 minutes. GitHub will display your site URL:
   `https://YOUR-USERNAME.github.io/vies-des-saints/`

---

### Step 6: Test the site locally

The site uses relative paths and works without any additional configuration.
To test locally, start an HTTP server from the `docs/` folder:

```bash
cd docs
python3 -m http.server 8080
```

Then open `http://localhost:8080` in your browser.

---

### Step 7: Add the Junicode font

The Junicode font is used for transcriptions. It must be downloaded and
placed in `docs/fonts/`.

1. Go to [github.com/psb1558/Junicode-font/releases](https://github.com/psb1558/Junicode-font/releases)
2. Download the latest release (`.zip` file)
3. Unzip it and open the `webfiles/` (or `webfonts/`) folder
4. Copy `JunicodeVF-Roman.woff2` and `JunicodeVF-Italic.woff2` into `docs/fonts/`
5. Commit and push via GitHub Desktop

---

### Step 8: Run the scraper manually

1. On GitHub, click the **Actions** tab
2. In the left list, click **Scrape Jonas Catalog**
3. Click the **Run workflow** button → **Run workflow**
4. Wait about 30 seconds
5. A green checkmark ✓ means everything worked and `manuscripts.json` has been updated

---

## Adding manuscripts

To add a manuscript to the corpus:

1. Search for the manuscript on [jonas.irht.cnrs.fr](https://jonas.irht.cnrs.fr)
2. Open the detail page and note the number in the URL: `...?projet=XXXXX`
3. Open `scraper/scrape_jonas.py` in a text editor
4. Add the number to the `MANUSCRIPT_IDS` list:
   ```python
   MANUSCRIPT_IDS = [
       71291,
       XXXXX,  # New manuscript
   ]
   ```
5. Commit and push, then re-run the workflow (Step 8)

---

## Local development (developers)

```bash
# Create the Python virtual environment
python3 -m venv .venv
source .venv/bin/activate      # Mac/Linux
# .venv\Scripts\activate.bat   # Windows

# Install dependencies
pip install -r scraper/requirements.txt

# Run the scraper
python scraper/scrape_jonas.py

# Test the site locally
cd docs
python3 -m http.server 8080
# Open http://localhost:8080
```

---

## Sources

- Jonas Catalog (IRHT–CNRS): [jonas.irht.cnrs.fr](https://jonas.irht.cnrs.fr)
- Junicode font: [github.com/psb1558/Junicode-font](https://github.com/psb1558/Junicode-font)
- Atkinson Hyperlegible font: [Google Fonts](https://fonts.google.com/specimen/Atkinson+Hyperlegible)
