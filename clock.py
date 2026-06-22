#!/usr/bin/env python3
import curses
import json
import locale
import os
import signal
import threading
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

locale.setlocale(locale.LC_ALL, "")

DEFAULT_CONFIG = {
    "time_format": "%H:%M:%S",
    "show_seconds": True,
    "blink_colon": True,
    "frame": True,
    "title": "RETRO CLOCK",
    "ticker": {
        "enabled": True,
        "mode": "rotate",
        "rotate_seconds": 10,
        "items_per_feed": 2,
        "refresh_minutes": 15,
        "max_items_per_feed": 8,
        "max_title_length": 120,
        "fallback_text": "RSS offline - waiting for feed data.",
        "feeds": [
            {
                "name": "Herr Montag Status",
                "url": "https://status.herrmontag.de/rss/"
            }
        ]
    }
}

DIGITS = {
    "0": [
        " ██████ ",
        "██    ██",
        "██    ██",
        "██    ██",
        "██    ██",
        "██    ██",
        " ██████ ",
    ],
    "1": [
        "   ██   ",
        " ████   ",
        "   ██   ",
        "   ██   ",
        "   ██   ",
        "   ██   ",
        " ██████ ",
    ],
    "2": [
        " ██████ ",
        "██    ██",
        "      ██",
        " ██████ ",
        "██      ",
        "██      ",
        "████████",
    ],
    "3": [
        " ██████ ",
        "██    ██",
        "      ██",
        "  █████ ",
        "      ██",
        "██    ██",
        " ██████ ",
    ],
    "4": [
        "██   ██ ",
        "██   ██ ",
        "██   ██ ",
        "████████",
        "     ██ ",
        "     ██ ",
        "     ██ ",
    ],
    "5": [
        "████████",
        "██      ",
        "██      ",
        "███████ ",
        "      ██",
        "██    ██",
        " ██████ ",
    ],
    "6": [
        " ██████ ",
        "██    ██",
        "██      ",
        "███████ ",
        "██    ██",
        "██    ██",
        " ██████ ",
    ],
    "7": [
        "████████",
        "     ██ ",
        "    ██  ",
        "   ██   ",
        "  ██    ",
        "  ██    ",
        "  ██    ",
    ],
    "8": [
        " ██████ ",
        "██    ██",
        "██    ██",
        " ██████ ",
        "██    ██",
        "██    ██",
        " ██████ ",
    ],
    "9": [
        " ██████ ",
        "██    ██",
        "██    ██",
        " ███████",
        "      ██",
        "██    ██",
        " ██████ ",
    ],
    ":": [
        "   ",
        " ██",
        " ██",
        "   ",
        " ██",
        " ██",
        "   ",
    ],
    " ": [
        "   ",
        "   ",
        "   ",
        "   ",
        "   ",
        "   ",
        "   ",
    ]
}

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "retro_terminal_clock_config.json")
RSS_FEEDS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rssfeed.conf")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OPML_FEEDS_PATH = os.path.join(BASE_DIR, "feeds.opml")


class TickerState:
    def __init__(self):
        self.lock = threading.Lock()
        self.entries = []
        self.fallback_text = DEFAULT_CONFIG["ticker"]["fallback_text"]
        self.last_refresh = None
        self.last_error = None

    def set_entries(self, entries, fallback_text, error=None):
        with self.lock:
            if entries:
                self.entries = entries
            self.fallback_text = fallback_text
            self.last_refresh = datetime.now()
            self.last_error = error

    def get_display_text(self, index):
        with self.lock:
            if self.entries:
                return self.entries[index % len(self.entries)]
            return self.fallback_text

    def has_entries(self):
        with self.lock:
            return bool(self.entries)


def deep_merge(base, override):
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def ensure_feed_conf():
    if os.path.exists(RSS_FEEDS_PATH):
        return
    lines = [
        "# RSS feeds for Retro Terminal Clock",
        "# Lines starting with # are ignored.",
        "# One feed block consists of name: and url: lines.",
        "",
        "name: Herr Montag Status",
        "url: https://status.herrmontag.de/rss/",
        "",
    ]
    with open(RSS_FEEDS_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))



def parse_feed_conf():
    feeds = []
    if not os.path.exists(RSS_FEEDS_PATH):
        return feeds

    current = {}
    with open(RSS_FEEDS_PATH, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                if current.get("name") and current.get("url"):
                    feeds.append({"name": current["name"], "url": current["url"]})
                    current = {}
                continue
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip().lower()
            value = value.strip()
            if key == "name":
                if current.get("name") and current.get("url"):
                    feeds.append({"name": current["name"], "url": current["url"]})
                    current = {}
                current["name"] = value
            elif key == "url":
                current["url"] = value

    if current.get("name") and current.get("url"):
        feeds.append({"name": current["name"], "url": current["url"]})

    return feeds



def find_opml_file():
    if os.path.exists(OPML_FEEDS_PATH):
        return OPML_FEEDS_PATH

    candidates = []
    try:
        for name in os.listdir(BASE_DIR):
            lower = name.lower()
            if lower.endswith('.opml') or lower.endswith('.opml.xml'):
                candidates.append(name)
    except Exception:
        return None

    if not candidates:
        return None

    candidates.sort()
    return os.path.join(BASE_DIR, candidates[0])



def parse_opml_feeds():
    feeds = []
    opml_path = find_opml_file()
    if not opml_path:
        return feeds

    try:
        tree = ET.parse(opml_path)
        root = tree.getroot()
    except Exception:
        return feeds

    for node in root.iter():
        if local_name(node.tag) != "outline":
            continue
        url = (node.attrib.get("xmlUrl") or node.attrib.get("xmlurl") or "").strip()
        if not url:
            continue
        name = (
            node.attrib.get("title")
            or node.attrib.get("text")
            or node.attrib.get("label")
            or url
        ).strip()
        feeds.append({"name": name, "url": url})

    return feeds



def ensure_config():
    ensure_feed_conf()
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        cfg = DEFAULT_CONFIG
    else:
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
            cfg = deep_merge(DEFAULT_CONFIG, user_cfg)
        except Exception:
            cfg = DEFAULT_CONFIG

    feeds_from_opml = parse_opml_feeds()
    if feeds_from_opml:
        cfg.setdefault("ticker", {})["feeds"] = feeds_from_opml
    else:
        feeds_from_conf = parse_feed_conf()
        if feeds_from_conf:
        cfg.setdefault("ticker", {})["feeds"] = feeds_from_conf
    return cfg


def draw_text(stdscr, y, x, text, attr=0, max_width=None):
    h, w = stdscr.getmaxyx()
    if y < 0 or y >= h:
        return
    if x >= w:
        return
    if max_width is None:
        max_width = w - max(0, x)
    if x < 0:
        text = text[-x:]
        max_width += x
        x = 0
    if max_width <= 0:
        return
    clipped = text[:max_width]
    try:
        stdscr.addstr(y, x, clipped, attr)
    except curses.error:
        pass


def render_big(text, colon_visible=True):
    rows = [""] * 7
    for ch in text:
        glyph = DIGITS.get(ch, DIGITS[" "])
        if ch == ":" and not colon_visible:
            glyph = DIGITS[" "]
        for i in range(7):
            rows[i] += glyph[i] + "  "
    return rows


def draw_split_flap(stdscr, top, left, rows, color_main, color_shadow):
    width = max(len(r) for r in rows)
    flap_y = top + 3
    for i, row in enumerate(rows):
        attr = color_main | curses.A_BOLD
        if i >= 4:
            attr = color_shadow | curses.A_BOLD
        draw_text(stdscr, top + i, left, row, attr, width)
    draw_text(stdscr, flap_y, left - 1, "-" * (width + 2), color_shadow)


def strip_text(value):
    if not value:
        return ""
    return " ".join(str(value).replace("\n", " ").replace("\r", " ").split())


def limit_text(text, max_len):
    text = strip_text(text)
    if max_len and len(text) > max_len:
        return text[: max_len - 1].rstrip() + "…"
    return text


def local_name(tag):
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def parse_feed_datetime(value):
    if not value:
        return None
    value = value.strip()
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)
    except Exception:
        pass
    try:
        return parsedate_to_datetime(value)
    except Exception:
        return None


def extract_rss_items(root, max_items, max_title_length):
    items = []
    channel = None
    for child in root:
        if local_name(child.tag) == "channel":
            channel = child
            break
    if channel is None:
        return items

    for item in channel:
        if local_name(item.tag) != "item":
            continue
        title = ""
        pub_date = None
        for node in item:
            name = local_name(node.tag)
            if name == "title":
                title = strip_text(node.text)
            elif name == "pubDate":
                pub_date = parse_feed_datetime(node.text)
        if title:
            items.append((pub_date or datetime.min, limit_text(title, max_title_length)))
        if len(items) >= max_items:
            break
    return items


def extract_atom_items(root, max_items, max_title_length):
    items = []
    for entry in root:
        if local_name(entry.tag) != "entry":
            continue
        title = ""
        pub_date = None
        for node in entry:
            name = local_name(node.tag)
            if name == "title":
                title = strip_text("".join(node.itertext()))
            elif name in ("updated", "published") and pub_date is None:
                pub_date = parse_feed_datetime(node.text)
        if title:
            items.append((pub_date or datetime.min, limit_text(title, max_title_length)))
        if len(items) >= max_items:
            break
    return items


def display_name_for_feed(feed_cfg):
    url = feed_cfg.get("url", "").strip()
    name = feed_cfg.get("name", "").strip()
    if name:
        return name
    if url:
        try:
            from urllib.parse import urlparse
            host = urlparse(url).netloc
            if host:
                return host
        except Exception:
            pass
    return "Feed"


def fetch_feed(feed_cfg, max_items, max_title_length):
    url = feed_cfg.get("url", "").strip()
    label = display_name_for_feed(feed_cfg)
    if not url:
        return []

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "retro-terminal-clock/1.1 (+https://github.com/thafaker)"
        },
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        data = response.read()

    root = ET.fromstring(data)
    root_name = local_name(root.tag)
    if root_name == "rss":
        entries = extract_rss_items(root, max_items, max_title_length)
    elif root_name == "feed":
        entries = extract_atom_items(root, max_items, max_title_length)
    else:
        entries = []

    return {
        "label": label,
        "items": entries,
    }


def fit_inline_titles(prefix, titles, width, min_second_title_width=18):
    usable = max(10, width - len(prefix))
    clean = [strip_text(t) for t in titles if strip_text(t)]
    if not clean:
        return prefix.rstrip()

    if len(clean) >= 2:
        separator = " | "
        reserve_for_second = len(separator) + min_second_title_width
        if usable > reserve_for_second:
            first_room = usable - reserve_for_second
            first = limit_text(clean[0], first_room)
            remaining = usable - len(first) - len(separator)
            if remaining >= min_second_title_width:
                second = limit_text(clean[1], remaining)
                candidate = prefix + first + separator + second
                if len(candidate) <= width:
                    return candidate

    first_only = limit_text(clean[0], usable)
    return prefix + first_only


def build_ticker_entries(cfg, display_width=78):
    ticker_cfg = cfg.get("ticker", {})
    feeds = ticker_cfg.get("feeds", [])
    max_items = max(1, int(ticker_cfg.get("max_items_per_feed", 8)))
    visible_items = max(1, int(ticker_cfg.get("items_per_feed", 2)))
    max_title_length = max(20, int(ticker_cfg.get("max_title_length", 120)))
    fallback = ticker_cfg.get("fallback_text", "RSS offline - waiting for feed data.")
    entries = []
    errors = []

    for feed in feeds:
        label = display_name_for_feed(feed)
        try:
            payload = fetch_feed(feed, max_items, max_title_length)
            titles = [title for _, title in payload["items"][:visible_items] if title]
            if titles:
                prefix = f"Ticker: {payload['label']}: "
                entries.append(fit_inline_titles(prefix, titles, display_width))
        except (urllib.error.URLError, TimeoutError, ET.ParseError, ValueError) as exc:
            errors.append(f"{label}: {exc}")
        except Exception as exc:
            errors.append(f"{label}: {exc}")

    if entries:
        return entries, None

    if errors:
        return [], "; ".join(errors)

    return [], "No feeds configured"


def refresh_ticker(cfg, ticker_state):
    ticker_cfg = cfg.get("ticker", {})
    fallback = ticker_cfg.get("fallback_text", "Ticker disabled")
    if not ticker_cfg.get("enabled", False):
        ticker_state.set_entries([], fallback, None)
        return
    display_width = 78 if cfg.get("frame", True) else 80
    entries, error = build_ticker_entries(cfg, display_width=display_width)
    ticker_state.set_entries(entries, fallback, error)


def ticker_worker(state):
    cfg = state["config"]
    ticker_state = state["ticker_state"]
    refresh_ticker(cfg, ticker_state)


def draw_centered_clock(stdscr, cfg, now, ticker_index, ticker_state):
    h, w = stdscr.getmaxyx()
    stdscr.erase()

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, -1)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_CYAN, -1)
    curses.init_pair(4, curses.COLOR_BLUE, -1)
    curses.init_pair(5, curses.COLOR_GREEN, -1)

    color_main = curses.color_pair(1)
    color_shadow = curses.color_pair(4)
    color_frame = curses.color_pair(3)
    color_title = curses.color_pair(5) | curses.A_BOLD

    if cfg.get("show_seconds", True):
        fmt = cfg.get("time_format", "%H:%M:%S")
    else:
        fmt = "%H:%M"
    time_text = now.strftime(fmt)

    colon_visible = True
    if cfg.get("blink_colon", True):
        colon_visible = now.second % 2 == 0

    big_rows = render_big(time_text, colon_visible=colon_visible)
    big_w = max(len(r) for r in big_rows)
    big_h = len(big_rows)

    top_pad = 1
    if cfg.get("ticker", {}).get("enabled", False):
        top_pad += 1
    if cfg.get("frame", True):
        top_pad += 1

    start_y = max(top_pad + 1, (h - big_h) // 2 - 1)
    start_x = max(0, (w - big_w) // 2)

    if cfg.get("frame", True) and h >= 3 and w >= 4:
        stdscr.box()

    title = cfg.get("title", "RETRO CLOCK")
    if cfg.get("frame", True):
        draw_text(stdscr, 0, max(2, (w - len(title)) // 2), f" {title} ", color_title)
    else:
        draw_text(stdscr, 0, max(0, (w - len(title)) // 2), title, color_title)

    if cfg.get("ticker", {}).get("enabled", False):
        ticker_str = ticker_state.get_display_text(ticker_index)
        y = 1 if cfg.get("frame", True) else 1
        x = 1 if cfg.get("frame", True) else 0
        max_width = max(1, w - 2 if cfg.get("frame", True) else w)
        draw_text(stdscr, y, x, ticker_str, color_frame | curses.A_BOLD, max_width)

    draw_split_flap(stdscr, start_y, start_x, big_rows, color_main, color_shadow)

    small = now.strftime("%A, %d %B %Y")
    small_y = start_y + big_h + 2
    if small_y < h - 1:
        draw_text(stdscr, small_y, max(0, (w - len(small)) // 2), small, color_frame)

    hint = "Q quit  |  C config reload  |  R refresh feeds"
    hint_y = h - 2 if cfg.get("frame", True) else h - 1
    if hint_y >= 0:
        draw_text(stdscr, hint_y, max(0, (w - len(hint)) // 2), hint, color_frame)

    if h < 18 or w < 70:
        warn = "Ideal size: 80x25"
        draw_text(stdscr, 2, max(0, (w - len(warn)) // 2), warn, curses.A_REVERSE)

    stdscr.refresh()


def start_refresh_thread(shared_state):
    worker = threading.Thread(target=ticker_worker, args=(shared_state,), daemon=True)
    worker.start()
    return worker


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    cfg = ensure_config()
    rotate_seconds = max(3, int(cfg.get("ticker", {}).get("rotate_seconds", 10)))
    ticker_index = 0
    last_rotate = time.monotonic()
    refresh_minutes = max(1, int(cfg.get("ticker", {}).get("refresh_minutes", 15)))
    next_refresh = time.monotonic()
    ticker_state = TickerState()
    shared_state = {"config": cfg, "ticker_state": ticker_state}
    refresh_thread = start_refresh_thread(shared_state)

    while True:
        now = datetime.now()
        ticker_enabled = cfg.get("ticker", {}).get("enabled", False)
        if ticker_enabled and ticker_state.has_entries():
            if time.monotonic() - last_rotate >= rotate_seconds:
                ticker_index += 1
                last_rotate = time.monotonic()
        else:
            last_rotate = time.monotonic()

        if ticker_enabled and time.monotonic() >= next_refresh and not refresh_thread.is_alive():
            shared_state = {"config": cfg, "ticker_state": ticker_state}
            refresh_thread = start_refresh_thread(shared_state)
            next_refresh = time.monotonic() + refresh_minutes * 60

        draw_centered_clock(stdscr, cfg, now, ticker_index, ticker_state)

        ch = stdscr.getch()
        if ch in (ord("q"), ord("Q")):
            break
        if ch in (ord("c"), ord("C")):
            cfg = ensure_config()
            rotate_seconds = max(3, int(cfg.get("ticker", {}).get("rotate_seconds", 10)))
            refresh_minutes = max(1, int(cfg.get("ticker", {}).get("refresh_minutes", 15)))
            next_refresh = time.monotonic()
            last_rotate = time.monotonic()
        if ch in (ord("r"), ord("R")) and not refresh_thread.is_alive():
            shared_state = {"config": cfg, "ticker_state": ticker_state}
            refresh_thread = start_refresh_thread(shared_state)
            next_refresh = time.monotonic() + refresh_minutes * 60


def run():
    signal.signal(signal.SIGINT, lambda sig, frame: exit(0))
    curses.wrapper(main)


if __name__ == "__main__":
    run()
