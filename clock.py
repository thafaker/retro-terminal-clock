#!/usr/bin/env python3
import curses
import json
import locale
import os
import signal
import time
from datetime import datetime

locale.setlocale(locale.LC_ALL, "")

DEFAULT_CONFIG = {
    "time_format": "%H:%M:%S",
    "show_seconds": True,
    "blink_colon": True,
    "frame": True,
    "title": "RETRO CLOCK",
    "ticker": {
        "enabled": False,
        "text": "RSS ticker disabled - add feeds later via config.",
        "speed_cps": 12,
        "padding": "   ***   "
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


def deep_merge(base, override):
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def ensure_config():
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            user_cfg = json.load(f)
        return deep_merge(DEFAULT_CONFIG, user_cfg)
    except Exception:
        return DEFAULT_CONFIG


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
    draw_text(stdscr, flap_y, left - 1, "─" * (width + 2), color_shadow)


def make_ticker_string(cfg):
    ticker = cfg.get("ticker", {})
    base = ticker.get("text", "")
    pad = ticker.get("padding", "   ")
    if not base:
        base = "RSS ticker disabled"
    return base + pad


def draw_centered_clock(stdscr, cfg, now, tick_offset):
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
        ticker_str = make_ticker_string(cfg)
        repeated = ticker_str * max(3, (w // max(1, len(ticker_str))) + 3)
        start = tick_offset % len(ticker_str)
        visible = repeated[start:start + max(1, w - 2)]
        y = 1 if cfg.get("frame", True) else 1
        x = 1 if cfg.get("frame", True) else 0
        draw_text(stdscr, y, x, visible, color_frame | curses.A_BOLD, max(1, w - 2 if cfg.get("frame", True) else w))

    draw_split_flap(stdscr, start_y, start_x, big_rows, color_main, color_shadow)

    small = now.strftime("%A, %d %B %Y")
    small_y = start_y + big_h + 2
    if small_y < h - 1:
        draw_text(stdscr, small_y, max(0, (w - len(small)) // 2), small, color_frame)

    hint = "Q quit  |  C config reload"
    hint_y = h - 2 if cfg.get("frame", True) else h - 1
    if hint_y >= 0:
        draw_text(stdscr, hint_y, max(0, (w - len(hint)) // 2), hint, color_frame)

    if h < 18 or w < 70:
        warn = "Ideal size: 80x25"
        draw_text(stdscr, 2, max(0, (w - len(warn)) // 2), warn, curses.A_REVERSE)

    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    cfg = ensure_config()
    ticker_speed = max(1, int(cfg.get("ticker", {}).get("speed_cps", 12)))
    tick_offset = 0
    last_tick = time.monotonic()

    while True:
        now = datetime.now()
        ticker_enabled = cfg.get("ticker", {}).get("enabled", False)
        if ticker_enabled:
            elapsed = time.monotonic() - last_tick
            step = int(elapsed * ticker_speed)
            if step > 0:
                tick_offset += step
                last_tick = time.monotonic()
        else:
            last_tick = time.monotonic()

        draw_centered_clock(stdscr, cfg, now, tick_offset)

        ch = stdscr.getch()
        if ch in (ord("q"), ord("Q")):
            break
        if ch in (ord("c"), ord("C")):
            cfg = ensure_config()
            ticker_speed = max(1, int(cfg.get("ticker", {}).get("speed_cps", 12)))


def run():
    signal.signal(signal.SIGINT, lambda sig, frame: exit(0))
    curses.wrapper(main)


if __name__ == "__main__":
    run()
