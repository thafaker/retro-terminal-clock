# Retro Terminal Clock

A retro terminal clock in a split-flap / flip-clock style, designed for an 80x25 terminal and prepared for a later RSS ticker extension.

## English

### Features

- large retro-style time display
- split-flap feel with a horizontal divider line
- designed for 80x25 terminals
- runs directly in the terminal
- no external Python dependencies
- prepared configuration structure for later ticker / RSS support
- reload configuration while the app is running

### Requirements

- Python 3.8 or newer
- a terminal with `curses` support
- recommended: 80x25 characters

Note:
It should work directly on Linux and macOS. On Windows, `curses` support depends on the environment and may not be available by default.

### Files

- `retro_terminal_clock.py` - main program
- `retro_terminal_clock_config.json` - created automatically on first launch

### Run

```bash
python3 retro_terminal_clock.py
```

### Controls

- `Q` - quit the program
- `C` - reload configuration
- `Ctrl+C` - exit immediately

### Configuration

On first launch, the program creates a file named `retro_terminal_clock_config.json` automatically.

Example:

```json
{
  "time_format": "%H:%M:%S",
  "show_seconds": true,
  "blink_colon": true,
  "frame": true,
  "title": "RETRO CLOCK",
  "ticker": {
    "enabled": false,
    "text": "RSS ticker disabled - add feeds later via config.",
    "speed_cps": 12,
    "padding": "   ***   "
  }
}
```

#### General options

- `time_format` - Python `strftime` format string for the clock
- `show_seconds` - show or hide seconds
- `blink_colon` - blink the separators every second
- `frame` - enable or disable the border frame
- `title` - top title line

#### Ticker options (prepared)

- `ticker.enabled` - enables the scrolling ticker line
- `ticker.text` - text that scrolls across the screen
- `ticker.speed_cps` - speed in characters per second
- `ticker.padding` - spacing between repeated ticker segments

### Target size

The clock is designed for a classic **80x25 terminal**. It still runs in smaller windows, but it will show a size hint.

### Roadmap

#### Version 1.1

- running retro terminal clock
- configuration reload
- ticker configuration prepared

#### Planned version 2

- load real RSS feeds from configuration
- refresh headlines periodically
- fallback behavior on network errors
- combine multiple feeds

#### Possible later extensions

- toggleable date display
- 12h / 24h mode
- color themes
- alarm or chime
- Docker setup
- packaging as a small CLI tool

### GitHub quick start

Minimal setup:

```bash
git init
git add retro_terminal_clock.py README.md
git commit -m "Initial commit: retro terminal clock"
```

If you do not want to commit the auto-generated config file, add a `.gitignore` like this:

```gitignore
retro_terminal_clock_config.json
__pycache__/
```

### License

Still open - MIT would be a good choice if you want to share the project freely on GitHub.

### Next step

Suggested next steps:

1. add a `.gitignore`
2. add a `LICENSE`
3. implement the RSS ticker
4. optionally add a screenshot or GIF for GitHub

---

## Deutsch

Eine Retro-Uhr fuer das Terminal im Split-Flap-/Klappzahlen-Stil, optimiert fuer ein 80x25-Terminal und vorbereitet fuer eine spaetere RSS-Ticker-Erweiterung.

### Features

- grosse Uhrzeit im Retro-Look
- Split-Flap-Anmutung mit horizontaler Trennkante
- fuer 80x25-Terminals gedacht
- laeuft direkt im Terminal
- keine externen Python-Abhaengigkeiten
- vorbereitete Konfiguration fuer spaeteren Ticker/RSS-Support
- Konfiguration waehrend der Laufzeit neu laden

### Voraussetzungen

- Python 3.8 oder neuer
- ein Terminal mit `curses`-Unterstuetzung
- empfohlen: 80x25 Zeichen

Hinweis:
Unter Linux und macOS funktioniert das direkt. Unter Windows ist `curses` je nach Umgebung eingeschraenkt oder nicht standardmaessig verfuegbar.

### Dateien

- `retro_terminal_clock.py` - Hauptprogramm
- `retro_terminal_clock_config.json` - wird beim ersten Start automatisch erzeugt

### Start

```bash
python3 retro_terminal_clock.py
```

### Steuerung

- `Q` - Programm beenden
- `C` - Konfiguration neu laden
- `Ctrl+C` - Programm sofort beenden

### Konfiguration

Beim ersten Start wird automatisch eine Datei namens `retro_terminal_clock_config.json` erzeugt.

Beispiel:

```json
{
  "time_format": "%H:%M:%S",
  "show_seconds": true,
  "blink_colon": true,
  "frame": true,
  "title": "RETRO CLOCK",
  "ticker": {
    "enabled": false,
    "text": "RSS ticker disabled - add feeds later via config.",
    "speed_cps": 12,
    "padding": "   ***   "
  }
}
```

#### Allgemeine Optionen

- `time_format` - Python-`strftime`-Format fuer die Uhrzeit
- `show_seconds` - Sekunden anzeigen oder ausblenden
- `blink_colon` - Doppelpunkte blinken im Sekundentakt
- `frame` - Rahmen um die Uhr ein-/ausschalten
- `title` - Titelzeile oben

#### Ticker-Optionen (vorbereitet)

- `ticker.enabled` - aktiviert die Laufzeile
- `ticker.text` - Text, der durchlaeuft
- `ticker.speed_cps` - Geschwindigkeit in Zeichen pro Sekunde
- `ticker.padding` - Abstand zwischen Wiederholungen des Tickertests

### Zielgroesse

Die Uhr ist fuer ein klassisches **80x25-Terminal** gestaltet. Bei kleineren Fenstern laeuft sie weiterhin, zeigt aber einen Hinweis an.

### Roadmap

#### Version 1.1

- laufende Retro-Terminal-Uhr
- Reload der Konfiguration
- Ticker-Konfiguration vorbereitet

#### Geplante Version 2

- echte RSS-Feeds aus der Konfiguration laden
- Headlines periodisch aktualisieren
- Fallback bei Netzwerkfehlern
- mehrere Feeds kombinieren

#### Moegliche spaetere Erweiterungen

- Datum umschaltbar
- 12h-/24h-Modus
- Farbschemata/Themes
- Wecker oder Chime
- Docker-Setup
- Installation als kleines CLI-Tool

### GitHub vorbereiten

Minimaler Ablauf:

```bash
git init
git add retro_terminal_clock.py README.md
git commit -m "Initial commit: retro terminal clock"
```

Wenn du die automatisch erzeugte Konfigurationsdatei nicht einchecken willst, lege eine `.gitignore` an:

```gitignore
retro_terminal_clock_config.json
__pycache__/
```

### Lizenz

Noch offen - du kannst z. B. MIT waehlen, wenn du das Projekt frei auf GitHub teilen willst.

### Naechster Schritt

Als Naechstes bietet sich an:

1. `.gitignore` anlegen
2. `LICENSE` hinzufuegen
3. RSS-Ticker implementieren
4. optional Screenshot oder GIF fuer GitHub ergaenzen
