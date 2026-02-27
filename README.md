# Vies des Saints — Manuscrits hagiographiques médiévaux

Prototype d'un site web de recherche pour les éditions numériques des Vies de saints
dans les manuscrits médiévaux en langue d'oïl.

---

## Structure du projet

```
vies-des-saints/
├── .github/workflows/scrape-jonas.yml   ← Automatisation (GitHub Actions)
├── docs/                                ← Site web (servi par GitHub Pages)
│   ├── index.html                       ← Page d'accueil (grille de saints)
│   ├── manuscripts.html                 ← Index des manuscrits (données Jonas)
│   ├── about.html                       ← À propos du projet
│   ├── css/style.css                    ← Styles (design médiéval)
│   ├── fonts/                           ← Police Junicode (à ajouter manuellement)
│   ├── images/                          ← Images des saints (SVG placeholder)
│   ├── js/manuscripts-table.js          ← Table triable/filtrable
│   ├── saints/                          ← Pages individuelles par saint
│   ├── transcriptions/                  ← Transcriptions numériques
│   └── data/manuscripts.json           ← Données scrappées de Jonas (auto-généré)
└── scraper/
    ├── scrape_jonas.py                  ← Script de scraping
    └── requirements.txt
```

---

## Mise en place — Guide pas à pas pour débutants

### Étape 1 : Créer un compte GitHub (si vous n'en avez pas)

1. Allez sur [github.com](https://github.com) et cliquez sur **Sign up**
2. Remplissez le formulaire et confirmez votre adresse e-mail
3. Choisissez le plan **Free**

---

### Étape 2 : Créer un nouveau dépôt

1. Sur votre page GitHub, cliquez sur le bouton vert **New** (ou allez sur github.com/new)
2. **Repository name** : choisissez un nom, par exemple `vies-des-saints`
3. **Visibility** : choisissez **Public** (obligatoire pour GitHub Pages gratuit)
4. Cochez **Add a README file**
5. Cliquez sur **Create repository**

---

### Étape 3 : Installer GitHub Desktop

GitHub Desktop est une application gratuite qui vous permet de gérer votre dépôt
sans ligne de commande.

1. Téléchargez-la sur [desktop.github.com](https://desktop.github.com)
2. Installez-la et connectez-vous avec votre compte GitHub
3. Cliquez sur **Clone a repository from the Internet...**
4. Choisissez votre dépôt `vies-des-saints` et sélectionnez un dossier sur votre ordinateur
5. Cliquez sur **Clone**

---

### Étape 4 : Copier les fichiers du projet

1. Ouvrez le dossier où vous avez cloné le dépôt
2. Copiez tous les fichiers et dossiers de ce projet dans ce dossier :
   - `.github/` (dossier caché — assurez-vous qu'il est inclus)
   - `docs/`
   - `scraper/`
   - `README.md`
3. Dans GitHub Desktop, vous verrez tous ces fichiers listés sous **Changes**
4. Tapez un message dans le champ **Summary**, par exemple : `Initial commit`
5. Cliquez sur **Commit to main**
6. Cliquez sur **Push origin** pour envoyer les fichiers sur GitHub

---

### Étape 5 : Configurer GitHub Pages

1. Sur GitHub, ouvrez votre dépôt et cliquez sur l'onglet **Settings** ⚙
2. Dans la barre gauche, cliquez sur **Pages**
3. Sous **Source**, choisissez **Deploy from a branch**
4. Sous **Branch**, sélectionnez **main** et le dossier **/ (docs)**
5. Cliquez sur **Save**
6. Attendez 1–2 minutes. GitHub affichera l'URL de votre site :
   `https://VOTRE-NOM.github.io/vies-des-saints/`

---

### Étape 6 : Mettre à jour le `<base href>` dans les fichiers HTML

Pour que les liens fonctionnent correctement sur GitHub Pages, ouvrez chaque fichier
HTML dans `docs/` (et ses sous-dossiers) et remplacez la ligne commentée :

```html
<!-- <base href="https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/"> -->
```

par (en retirant les `<!--` et `-->` et en remplaçant les placeholders) :

```html
<base href="https://VOTRE-NOM.github.io/vies-des-saints/">
```

Faites cela pour tous les fichiers HTML, puis committez et pushez via GitHub Desktop.

> **Astuce** : Pour tester en local sans modifier le `<base href>`, lancez un serveur
> HTTP local depuis le dossier `docs/` :
> ```bash
> python3 -m http.server 8080
> ```
> Puis ouvrez `http://localhost:8080` dans votre navigateur.

---

### Étape 7 : Ajouter la police Junicode

La police Junicode est utilisée pour les transcriptions. Elle doit être téléchargée et
placée dans `docs/fonts/`.

1. Allez sur [github.com/psb1558/Junicode-font/releases](https://github.com/psb1558/Junicode-font/releases)
2. Téléchargez la dernière version (fichier `.zip`)
3. Décompressez le ZIP et ouvrez le dossier `webfiles/` (ou `webfonts/`)
4. Copiez `JunicodeVF-Roman.woff2` et `JunicodeVF-Italic.woff2` dans `docs/fonts/`
5. Committez et pushez via GitHub Desktop

---

### Étape 8 : Lancer le scraper manuellement

1. Sur GitHub, cliquez sur l'onglet **Actions**
2. Dans la liste à gauche, cliquez sur **Scrape Jonas Catalog**
3. Cliquez sur le bouton **Run workflow** → **Run workflow**
4. Attendez environ 30 secondes
5. Une coche verte ✓ indique que tout s'est bien passé et que `manuscripts.json` a été mis à jour

---

## Ajouter des manuscrits

Pour ajouter un manuscrit au corpus :

1. Recherchez le manuscrit sur [jonas.irht.cnrs.fr](https://jonas.irht.cnrs.fr)
2. Ouvrez la page de détail et notez le numéro dans l'URL : `...?projet=XXXXX`
3. Ouvrez `scraper/scrape_jonas.py` dans un éditeur de texte
4. Ajoutez le numéro à la liste `MANUSCRIPT_IDS` :
   ```python
   MANUSCRIPT_IDS = [
       71291,
       XXXXX,  # Nouveau manuscrit
   ]
   ```
5. Committez et pushez, puis relancez le workflow (Étape 8)

---

## Test local (développeurs)

```bash
# Créer l'environnement virtuel Python
python3 -m venv .venv
source .venv/bin/activate      # Mac/Linux
# .venv\Scripts\activate.bat   # Windows

# Installer les dépendances
pip install -r scraper/requirements.txt

# Lancer le scraper
python scraper/scrape_jonas.py

# Tester le site en local
cd docs
python3 -m http.server 8080
# Ouvrir http://localhost:8080
```

---

## Sources

- Catalogue Jonas (IRHT–CNRS) : [jonas.irht.cnrs.fr](https://jonas.irht.cnrs.fr)
- Police Junicode : [github.com/psb1558/Junicode-font](https://github.com/psb1558/Junicode-font)
- Police Atkinson Hyperlegible : [Google Fonts](https://fonts.google.com/specimen/Atkinson+Hyperlegible)
