# Retro Terminal Clock

A retro terminal clock in a split-flap / flip-clock style for an **80x25 terminal**, featuring a large clock display and a rotating RSS headline bar at the top.

## English

### Features

- large retro-style clock display
- split-flap look with a horizontal divider line
- designed around a classic **80x25** terminal layout
- rotating RSS headline bar instead of an old-school scrolling marquee
- feed rotation from an external `rssfeed.conf`
- automatic truncation of long headlines with `…`
- smart layout: shows a second headline only if it fits cleanly
- configuration reload while the app is running
- manual feed refresh while the app is running
- no external Python dependencies

### Requirements

- Python 3.8 or newer
- a terminal with `curses` support
- recommended terminal size: **80x25**

Note:
It should work directly on Linux and macOS. On Windows, `curses` support depends on the environment and may not be available by default.

### Files

- `clock.py` - main program
- `retro_terminal_clock_config.json` - runtime settings
- `rssfeed.conf` - RSS feed list
- `README.md` - documentation

### Run

```bash
python3 clock.py
```

### Controls

- `Q` - quit the program
- `C` - reload configuration and feed definitions
- `R` - refresh RSS feeds immediately
- `Ctrl+C` - exit immediately

### How the ticker works

The feed area appears in the **top inner line** below the title.

Example:

```text
Ticker: Herr Montag Status: Desk Sharing | Kater
```

Behavior:

- feeds are shown **one after another**
- each feed gets its own turn in the top line
- by default, up to **2 headlines** per feed are shown
- if 2 headlines do not fit nicely in **80x25**, the app falls back to **1 headline**
- long headlines are shortened with `…`
- the app does **not** use a continuous horizontal marquee

### Configuration

There are **two config files**:

#### 1. App settings: `retro_terminal_clock_config.json`

This file controls general behavior such as title, clock format, frame, refresh interval, and rotation timing.

Example:

```json
{
  "time_format": "%H:%M:%S",
  "show_seconds": true,
  "blink_colon": true,
  "frame": true,
  "title": "RETRO CLOCK",
  "ticker": {
    "enabled": true,
    "mode": "rotate",
    "rotate_seconds": 10,
    "items_per_feed": 2,
    "refresh_minutes": 15,
    "max_items_per_feed": 8,
    "max_title_length": 120,
    "fallback_text": "RSS offline - waiting for feed data."
  }
}
```

##### General options

- `time_format` - Python `strftime` format string for the clock
- `show_seconds` - show or hide seconds
- `blink_colon` - blink the separators every second
- `frame` - enable or disable the border frame
- `title` - top title line

##### Ticker options

- `ticker.enabled` - enable or disable the RSS ticker
- `ticker.mode` - current display mode, intended as `rotate`
- `ticker.rotate_seconds` - how long one feed stays visible before switching to the next
- `ticker.items_per_feed` - preferred number of headlines per feed
- `ticker.refresh_minutes` - how often feeds are refreshed automatically
- `ticker.max_items_per_feed` - number of fetched feed entries per source
- `ticker.max_title_length` - hard per-title limit before layout trimming
- `ticker.fallback_text` - text shown when no feed data is available

#### 2. Feed list: `rssfeed.conf`

This file contains the RSS sources in a simple editable format.

Example:

```text
# RSS feeds for Retro Terminal Clock
# Lines starting with # are ignored.

name: Herr Montag Status
url: https://status.herrmontag.de/rss/

name: Another Feed
url: https://example.com/rss.xml
```

Rules:

- lines starting with `#` are comments
- empty lines are allowed
- each feed uses:
  - `name:`
  - `url:`
- feeds are loaded in order and displayed in rotation

### Caching behavior

At the moment, feed entries are cached **in memory only** while the program is running.

That means:

- successful feed data stays available during runtime
- if a later refresh fails, existing entries can still remain visible
- after quitting the program, the cache is gone
- there is currently **no on-disk cache file**

### Target size

The clock is designed for a classic **80x25 terminal**. If the window is smaller, it still runs but may show a size warning and has less room for ticker content.

### GitHub quick start

Minimal setup:

```bash
git init
git add clock.py README.md retro_terminal_clock_config.json rssfeed.conf
git commit -m "Initial commit: retro terminal clock"
```

If you do not want to commit generated or local-only files, use a `.gitignore` that fits your setup.

### License

Still open - MIT would be a good choice if you want to share the project freely on GitHub.

### Roadmap ideas

- persistent RSS cache file
- theme variants
- optional date modes
- alarm or chime
- packaging as a small CLI tool

---

## Deutsch

Eine Retro-Uhr im Split-Flap-/Klappzahlen-Stil fuer ein **80x25-Terminal** mit grosser Zeitanzeige und einer rotierenden RSS-Kopfzeile im oberen Bereich.

### Features

- grosse Uhrzeit im Retro-Look
- Split-Flap-Anmutung mit horizontaler Trennkante
- auf ein klassisches **80x25-Terminal** ausgelegt
- rotierende RSS-Kopfzeile statt alter HTML-Laufschrift
- Feed-Rotation ueber eine externe `rssfeed.conf`
- lange Headlines werden sauber mit `…` gekuerzt
- intelligente Darstellung: ein zweiter Titel wird nur gezeigt, wenn er sauber hineinpasst
- Konfiguration waehrend der Laufzeit neu laden
- RSS-Feeds waehrend der Laufzeit manuell aktualisieren
- keine externen Python-Abhaengigkeiten

### Voraussetzungen

- Python 3.8 oder neuer
- ein Terminal mit `curses`-Unterstuetzung
- empfohlene Terminalgroesse: **80x25**

Hinweis:
Unter Linux und macOS funktioniert das direkt. Unter Windows ist `curses` je nach Umgebung eingeschraenkt oder nicht standardmaessig verfuegbar.

### Dateien

- `clock.py` - Hauptprogramm
- `retro_terminal_clock_config.json` - Laufzeit-Einstellungen
- `rssfeed.conf` - RSS-Feed-Liste
- `README.md` - Dokumentation

### Start

```bash
python3 clock.py
```

### Bedienung

- `Q` - Programm beenden
- `C` - Konfiguration und Feed-Definitionen neu laden
- `R` - RSS-Feeds sofort aktualisieren
- `Ctrl+C` - Programm sofort beenden

### So funktioniert der Ticker

Der Feed-Bereich erscheint in der **obersten Innenzeile** direkt unter Titel und Rahmen.

Beispiel:

```text
Ticker: Herr Montag Status: Desk Sharing | Kater
```

Verhalten:

- Feeds werden **nacheinander** angezeigt
- jeder Feed bekommt seinen eigenen Durchlauf in der oberen Zeile
- standardmaessig werden bis zu **2 Headlines** pro Feed gezeigt
- wenn 2 Headlines in **80x25** nicht sauber passen, faellt die Anzeige auf **1 Headline** zurueck
- lange Titel werden mit `…` gekuerzt
- es gibt **keine** durchlaufende horizontale Laufschrift mehr

### Konfiguration

Es gibt jetzt **zwei Konfigurationsdateien**:

#### 1. App-Einstellungen: `retro_terminal_clock_config.json`

Diese Datei steuert allgemeines Verhalten wie Titel, Uhrzeitformat, Rahmen, Aktualisierungsintervall und Rotationsdauer.

Beispiel:

```json
{
  "time_format": "%H:%M:%S",
  "show_seconds": true,
  "blink_colon": true,
  "frame": true,
  "title": "RETRO CLOCK",
  "ticker": {
    "enabled": true,
    "mode": "rotate",
    "rotate_seconds": 10,
    "items_per_feed": 2,
    "refresh_minutes": 15,
    "max_items_per_feed": 8,
    "max_title_length": 120,
    "fallback_text": "RSS offline - waiting for feed data."
  }
}
```

##### Allgemeine Optionen

- `time_format` - Python-`strftime`-Format fuer die Uhrzeit
- `show_seconds` - Sekunden anzeigen oder ausblenden
- `blink_colon` - Doppelpunkte blinken im Sekundentakt
- `frame` - Rahmen um die Uhr ein-/ausschalten
- `title` - Titelzeile oben

##### Ticker-Optionen

- `ticker.enabled` - RSS-Ticker ein- oder ausschalten
- `ticker.mode` - aktueller Anzeigemodus, vorgesehen ist `rotate`
- `ticker.rotate_seconds` - wie lange ein Feed sichtbar bleibt, bevor zum naechsten gewechselt wird
- `ticker.items_per_feed` - bevorzugte Anzahl an Headlines pro Feed
- `ticker.refresh_minutes` - automatische Aktualisierung der Feeds in Minuten
- `ticker.max_items_per_feed` - Anzahl geladener Feed-Eintraege pro Quelle
- `ticker.max_title_length` - harte Titelgrenze vor dem finalen Layout-Kuerzen
- `ticker.fallback_text` - Text, wenn keine Feed-Daten verfuegbar sind

#### 2. Feed-Liste: `rssfeed.conf`

Diese Datei enthaelt die RSS-Quellen in einem einfachen editierbaren Format.

Beispiel:

```text
# RSS feeds for Retro Terminal Clock
# Lines starting with # are ignored.

name: Herr Montag Status
url: https://status.herrmontag.de/rss/

name: Another Feed
url: https://example.com/rss.xml
```

Regeln:

- Zeilen mit `#` am Anfang sind Kommentare
- Leerzeilen sind erlaubt
- jeder Feed besteht aus:
  - `name:`
  - `url:`
- Feeds werden in dieser Reihenfolge geladen und rotiert angezeigt

### Cache-Verhalten

Aktuell werden Feed-Eintraege **nur im Arbeitsspeicher** zwischengespeichert, solange das Programm laeuft.

Das bedeutet:

- erfolgreich geladene Feed-Daten bleiben waehrend der Laufzeit verfuegbar
- wenn eine spaetere Aktualisierung fehlschlaegt, koennen vorhandene Eintraege weiter sichtbar bleiben
- nach dem Beenden des Programms ist dieser Cache weg
- aktuell gibt es **keine Cache-Datei auf der Platte**

### Zielgroesse

Die Uhr ist fuer ein klassisches **80x25-Terminal** gebaut. In kleineren Fenstern laeuft sie zwar weiter, hat aber weniger Platz fuer die Ticker-Zeile und kann einen Groessenhinweis anzeigen.

### GitHub vorbereiten

Minimaler Ablauf:

```bash
git init
git add clock.py README.md retro_terminal_clock_config.json rssfeed.conf
git commit -m "Initial commit: retro terminal clock"
```

Wenn du generierte oder rein lokale Dateien nicht einchecken willst, nutze eine passende `.gitignore`.

### Lizenz

Noch offen - MIT waere eine gute Wahl, wenn du das Projekt frei auf GitHub teilen willst.

### Roadmap-Ideen

- persistente RSS-Cache-Datei
- Theme-Varianten
- optionale Datumsmodi
- Wecker oder Chime
- Paketierung als kleines CLI-Tool
