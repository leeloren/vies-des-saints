/**
 * manuscripts-table.js
 * Loads docs/data/manuscripts.json and renders the sortable,
 * filterable manuscripts index table.
 *
 * No external dependencies — vanilla JS only.
 */
(function () {
  'use strict';

  // ── State ────────────────────────────────────────────────────────────────
  var allManuscripts = [];
  var sortCol = 'shelfmark';
  var sortDir = 'asc';

  // Mapping from saint IDs to display labels
  var SAINT_LABELS = {
    'saint-martin':    'Saint Martin',
    'saint-catherine': 'Sainte Catherine',
    'saint-nicholas':  'Saint Nicolas',
    'saint-margaret':  'Sainte Marguerite'
  };

  // ── Entry point ──────────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    loadData();
    setupSortHeaders();
    setupFilterControls();
  });

  // ── Data loading ─────────────────────────────────────────────────────────
  function loadData() {
    // Determine the correct path to the JSON file.
    // When served from /docs via GitHub Pages, the base URL points to the
    // repo root, so the path is data/manuscripts.json relative to the page.
    var jsonPath = 'data/manuscripts.json';

    fetch(jsonPath)
      .then(function (resp) {
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        return resp.json();
      })
      .then(function (data) {
        allManuscripts = data;
        applyFiltersAndSort();
      })
      .catch(function (err) {
        console.error('Failed to load manuscripts.json:', err);
        var tbody = document.getElementById('ms-table-body');
        tbody.innerHTML =
          '<tr><td colspan="6" style="text-align:center; color: var(--color-red); padding: 2rem;">' +
          'Erreur lors du chargement des données. ' +
          'Si vous testez en local, lancez un serveur HTTP&nbsp;: ' +
          '<code>python3 -m http.server 8080</code> depuis le dossier <code>docs/</code>.' +
          '</td></tr>';
      });
  }

  // ── Rendering ────────────────────────────────────────────────────────────
  function renderTable(data) {
    var tbody = document.getElementById('ms-table-body');
    var countEl = document.getElementById('ms-count-display');

    if (data.length === 0) {
      tbody.innerHTML =
        '<tr><td colspan="6" style="text-align:center; color: var(--color-text-muted); ' +
        'font-style: italic; padding: 2rem;">Aucun manuscrit ne correspond aux critères.</td></tr>';
      countEl.textContent = '0 manuscrit affiché';
      return;
    }

    var rows = data.map(function (ms) {
      var shelfmarkCell = ms.transcription_file
        ? '<a href="' + ms.transcription_file + '">' + escHtml(ms.shelfmark) + '</a>'
        : escHtml(ms.shelfmark);

      var saintTags = (ms.saints || []).map(function (s) {
        var label = SAINT_LABELS[s] || s;
        return '<span class="saint-tag"><a href="saints/' + escHtml(s) + '.html">' +
               escHtml(label) + '</a></span>';
      }).join(' ');

      var links = '<a href="' + escHtml(ms.jonas_url) + '" target="_blank" ' +
                  'rel="noopener" class="ext-link">Jonas</a>';

      return '<tr>' +
        '<td class="shelfmark-cell">' + shelfmarkCell + '</td>' +
        '<td>' + escHtml(ms.date_short || ms.date || '—') + '</td>' +
        '<td>' + escHtml(ms.support || '—') + '</td>' +
        '<td>' + escHtml(ms.origin || '—') + '</td>' +
        '<td>' + (saintTags || '<span style="color:var(--color-text-muted)">—</span>') + '</td>' +
        '<td>' + links + '</td>' +
        '</tr>';
    });

    tbody.innerHTML = rows.join('');

    var n = data.length;
    countEl.textContent = n + ' manuscrit' + (n > 1 ? 's' : '') + ' affiché' + (n > 1 ? 's' : '');
  }

  // ── Filtering & sorting ──────────────────────────────────────────────────
  function applyFiltersAndSort() {
    var searchVal  = (document.getElementById('ms-search').value || '').toLowerCase().trim();
    var suppVal    = document.getElementById('ms-filter-support').value;
    var saintVal   = document.getElementById('ms-filter-saint').value;

    var filtered = allManuscripts.filter(function (ms) {
      // Text search: shelfmark, origin, language
      if (searchVal) {
        var haystack = [ms.shelfmark, ms.origin, ms.language, ms.script]
          .join(' ').toLowerCase();
        if (haystack.indexOf(searchVal) === -1) return false;
      }
      // Support filter
      if (suppVal && (ms.support || '') !== suppVal) return false;
      // Saint filter
      if (saintVal && (ms.saints || []).indexOf(saintVal) === -1) return false;

      return true;
    });

    // Sort
    filtered.sort(function (a, b) {
      var valA = String(a[sortCol] || '').toLowerCase();
      var valB = String(b[sortCol] || '').toLowerCase();
      var cmp = valA.localeCompare(valB, 'fr', { sensitivity: 'base' });
      return sortDir === 'asc' ? cmp : -cmp;
    });

    renderTable(filtered);
  }

  // ── Sort header setup ────────────────────────────────────────────────────
  function setupSortHeaders() {
    var headers = document.querySelectorAll('#ms-table th.sortable');
    headers.forEach(function (th) {
      th.style.cursor = 'pointer';
      th.addEventListener('click', function () {
        var col = th.dataset.col;
        if (sortCol === col) {
          sortDir = sortDir === 'asc' ? 'desc' : 'asc';
        } else {
          sortCol = col;
          sortDir = 'asc';
        }
        // Update visual indicator
        headers.forEach(function (h) {
          h.classList.remove('sort-asc', 'sort-desc');
        });
        th.classList.add(sortDir === 'asc' ? 'sort-asc' : 'sort-desc');
        applyFiltersAndSort();
      });
    });
  }

  // ── Filter control setup ─────────────────────────────────────────────────
  function setupFilterControls() {
    ['ms-search', 'ms-filter-support', 'ms-filter-saint'].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) {
        el.addEventListener('input', applyFiltersAndSort);
        el.addEventListener('change', applyFiltersAndSort);
      }
    });
  }

  // ── Utility ──────────────────────────────────────────────────────────────
  function escHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

})();
