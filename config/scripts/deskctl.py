#!/usr/bin/env python3
import curses
import json
import os
import tempfile
import time
import re
import shlex
import shutil
import subprocess
import sys
import threading
from functools import lru_cache
from pathlib import Path


HOME = Path.home()
CONFIG = HOME / ".config"

PICOM = CONFIG / "picom" / "picom.conf"
DESKCTL_CONFIG = CONFIG / "deskctl"
DISPLAY_BRIGHTNESS = DESKCTL_CONFIG / "display-brightness"
SESSION_STATE = DESKCTL_CONFIG / "session-state.json"
DWM = CONFIG / "dwm"
DMENU = CONFIG / "dmenu"
DMENU_LAUNCHER = DMENU / "dmenu-launcher.sh"
WALLPAPER_DIR = HOME / "Images/Wallpapers"
FEHBG = HOME / ".fehbg"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
FEH_MODE = "--bg-scale"
CORNER_RADII = ("0", "6", "10", "14")
OPACITY_VALUES = ("0.7", "0.8", "0.9", "1.0")
BRIGHTNESS_VALUES = ("0.35", "0.45", "0.55", "0.65", "0.75", "0.85", "1.0")
BACKENDS = ('"glx"', '"xrender"')
ACCENT_COLORS = (
    ("RED", "#f38ba8"),
    ("ORANGE", "#fab387"),
    ("BROWN", "#b08968"),
    ("YELLOW", "#f9e2af"),
    ("PINK", "#cba6f7"),
    ("PURPLE", "#b4befe"),
    ("BLUE", "#00ffff"),
    ("GREEN", "#a6e3a1"),
    ("WHITE", "#ffffff"),
)
DWM_ACCENT_PROPERTY = "_DWM_ACCENT"


def read(path):
    return path.read_text()


def write(path, text):
    path.write_text(text)


def run(cmd, cwd=None):
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return proc.returncode, proc.stdout.strip()


def command_exists(command):
    return shutil.which(command) is not None


def next_value(current, values):
    if current == "1" and "1.0" in values:
        current = "1.0"
    try:
        idx = values.index(current)
    except ValueError:
        return values[0]
    return values[(idx + 1) % len(values)]


def previous_value(current, values):
    if current == "1" and "1.0" in values:
        current = "1.0"
    try:
        idx = values.index(current)
    except ValueError:
        return values[0]
    return values[(idx - 1) % len(values)]


def stepped_value(current, values, direction):
    try:
        idx = values.index(current)
    except ValueError:
        return values[0]
    idx = max(0, min(len(values) - 1, idx + direction))
    return values[idx]


def replace_define(text, name, value):
    pat = rf'(static const char {re.escape(name)}\[\]\s*=\s*)"#(?:[0-9a-fA-F]{{6}})"'
    return re.sub(pat, rf'\1"{value}"', text)


def set_picom_key(text, key, value):
    pat = rf'(?m)^{re.escape(key)}\s*=\s*[^;]+;'
    line = f"{key} = {value};"
    if re.search(pat, text):
        return re.sub(pat, line, text)
    if text and not text.endswith("\n"):
        text += "\n"
    return text + line + "\n"


def remove_picom_key(text, key):
    return re.sub(rf'(?m)^{re.escape(key)}\s*=\s*[^;]+;\n?', "", text)


def remove_picom_list_item(text, key, item):
    def repl(match):
        values = [value.strip() for value in match.group(1).split(",")]
        values = [value for value in values if value.strip('"') != item]
        if not values:
            return ""
        return f"{key} = [ {', '.join(values)} ];"

    return re.sub(rf'(?m)^{re.escape(key)}\s*=\s*\[(.*?)\];\n?', repl, text)


def get_picom_key(text, key, default=""):
    m = re.search(rf'(?m)^{re.escape(key)}\s*=\s*([^;]+);', text)
    return m.group(1).strip() if m else default


def remove_block(text, name):
    pat = rf'(?ms)^\s*{re.escape(name)}\s*:\s*\{{.*?^\s*\}}\s*\n*'
    return re.sub(pat, "", text)


def has_block(text, name):
    return re.search(rf'(?m)^\s*{re.escape(name)}\s*:', text) is not None


def set_rule_property(text, match, key, value):
    rule_pat = re.compile(
        rf'(?ms)(\{{\s*match\s*=\s*"{re.escape(match)}";)(.*?)(\n\}})'
    )
    m = rule_pat.search(text)
    if m:
        body = m.group(2)
        prop_pat = rf'(?m)^(\s*){re.escape(key)}\s*=\s*[^;]+;'
        if re.search(prop_pat, body):
            body = re.sub(prop_pat, rf'\1{key} = {value};', body)
        else:
            body = body.rstrip() + f"\n  {key} = {value};"
        return text[:m.start()] + m.group(1) + body + m.group(3) + text[m.end():]

    rule = f'{{\n  match = "{match}";\n  {key} = {value};\n}}'
    m = re.search(r"(?ms)(rules:\s*\()(.*?)(\s*\)\s*)$", text)
    if m:
        sep = "" if not m.group(2).strip() else ", "
        return text[:m.start(3)] + sep + rule + text[m.start(3):]
    return text.rstrip() + "\n\nrules: (" + rule + ")\n"


def remove_rule_property(text, match, key):
    rule_pat = re.compile(
        rf'(?ms)(\{{\s*match\s*=\s*"{re.escape(match)}";)(.*?)(\n\}})'
    )
    m = rule_pat.search(text)
    if not m:
        return text

    body = re.sub(
        rf'(?m)^\s*{re.escape(key)}\s*=\s*[^;]+;\n?',
        "",
        m.group(2),
    ).rstrip()
    return text[:m.start()] + m.group(1) + body + m.group(3) + text[m.end():]


def remove_empty_rule(text, match):
    empty = rf'\{{\s*match\s*=\s*"{re.escape(match)}";\s*\}}'
    text = re.sub(rf'(?ms)(rules:\s*\()\s*{empty}\s*,\s*', r'\1', text)
    return re.sub(rf'(?ms),\s*{empty}', "", text)


def blur_enabled(text):
    return get_picom_key(text, "blur-background", "false") == "true" or has_block(text, "blur")


def inactive_opacity(text):
    m = re.search(
        r'(?ms)\{\s*match\s*=\s*"!focused && !group_focused";.*?^\s*opacity\s*=\s*([^;]+);',
        text,
    )
    if m:
        return m.group(1).strip()
    m = re.search(r'(?ms)\{\s*match\s*=\s*"!focused";.*?^\s*opacity\s*=\s*([^;]+);', text)
    return m.group(1).strip() if m else get_picom_key(text, "inactive-opacity", "1")


def active_opacity(text):
    m = re.search(
        r'(?ms)\{\s*match\s*=\s*"focused \|\| group_focused";.*?^\s*opacity\s*=\s*([^;]+);',
        text,
    )
    return m.group(1).strip() if m else get_picom_key(text, "active-opacity", "1.0")


@lru_cache(maxsize=1)
def wallpaper_images():
    if not WALLPAPER_DIR.exists():
        return []
    return sorted(
        (
            path for path in WALLPAPER_DIR.rglob("*")
            if path.is_file() and path.suffix.lower() in IMAGE_EXTS
        ),
        key=lambda path: str(path.relative_to(WALLPAPER_DIR)).lower(),
    )


def update_wallpaper_startup(path):
    FEHBG.write_text(
        "#!/bin/sh\n"
        f"feh --no-fehbg {FEH_MODE} {shlex.quote(str(path))}\n"
    )
    FEHBG.chmod(0o755)


def set_wallpaper(path):
    if not command_exists("feh"):
        return "error: feh is not installed"

    code, out = run(["feh", FEH_MODE, str(path)])
    if code != 0:
        return f"error: {out or 'failed to set wallpaper'}"

    update_wallpaper_startup(path)
    if command_exists("notify-send"):
        run(["notify-send", "Wallpaper set", path.name])
    return f"wallpaper set: {path.name}"


def accent_color():
    return match_value(
        read(DWM / "config.h"),
        r'static const char col_cyan\[\]\s*=\s*"(#[0-9a-fA-F]{6})"',
        "unset",
    )


def set_mc_accent(value):
    name = next((name.lower() for name, color in ACCENT_COLORS
                 if color.lower() == value.lower()), None)
    if name is None:
        return
    skin = f"deskctl-accent-{name}"
    path = CONFIG / "mc" / "ini"
    text = read(path) if path.exists() else ""
    section = re.search(r"(?ms)^\[Midnight-Commander\][^\n]*\n.*?(?=^\[|\Z)", text)
    if section:
        block = section.group()
        if re.search(r"(?m)^skin\s*=", block):
            block = re.sub(r"(?m)^skin\s*=.*$", f"skin={skin}", block)
        else:
            block = block.rstrip() + f"\nskin={skin}\n\n"
        text = text[:section.start()] + block + text[section.end():]
    else:
        text = text.rstrip() + f"\n[Midnight-Commander]\nskin={skin}\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    write(path, text)


def set_accent_color(value):
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        raise ValueError("color must use the format #RRGGBB")

    dwm_path = DWM / "config.h"
    dwm_text = read(dwm_path)
    if not re.search(r'static const char col_cyan\[\]\s*=\s*"#[0-9a-fA-F]{6}"', dwm_text):
        raise ValueError("could not find dwm col_cyan")

    launcher_text = read(DMENU_LAUNCHER)
    launcher_pattern = re.compile(r"(-sb\s+)(['\"])#[0-9a-fA-F]{6}\2")
    if not launcher_pattern.search(launcher_text):
        raise ValueError("could not find dmenu launcher -sb color")

    write(dwm_path, replace_define(dwm_text, "col_cyan", value))
    write(
        DMENU_LAUNCHER,
        launcher_pattern.sub(lambda match: f"{match.group(1)}{match.group(2)}{value}{match.group(2)}", launcher_text),
    )
    set_mc_accent(value)
    # The launcher passes its colors at startup, so dmenu needs no rebuild.
    # Patched dwm watches this root-window property and swaps its live scheme.
    code, output = run(
        ["xprop", "-root", "-f", DWM_ACCENT_PROPERTY, "8s", "-set", DWM_ACCENT_PROPERTY, value]
    )
    if code != 0:
        raise RuntimeError(f"colors saved, but live dwm update failed: {output or 'xprop failed'}")
    return f"dwm and dmenu color changed to {value}; MC skin saved (reopen MC)"


def match_value(text, pattern, default):
    m = re.search(pattern, text)
    return m.group(1) if m else default


def stop_picom():
    selector = ["-u", str(os.getuid()), "-x", "picom"]
    code, output = run(["pkill", *selector])
    if code not in (0, 1):
        raise RuntimeError(output or "could not stop picom")
    for _ in range(20):
        code, output = run(["pgrep", *selector])
        if code == 1:
            break
        if code != 0:
            raise RuntimeError(output or "could not check picom")
        time.sleep(0.05)
    else:
        raise RuntimeError("picom did not stop; replacement was not started")
    return "picom stopped (all effects off)"


def sync_picom():
    text = read(PICOM)
    needed = (
        blur_enabled(text)
        or any(get_picom_key(text, key, default) == "true"
               for key, default in (("shadow", "false"), ("fading", "false"), ("vsync", "true")))
        or float(active_opacity(text)) < 1.0
        or float(inactive_opacity(text)) < 1.0
        or float(get_picom_key(text, "corner-radius", "0")) > 0
    )
    if not needed:
        return stop_picom()
    return restart_picom()


def restart_picom():
    if not command_exists("picom"):
        raise RuntimeError("picom is not installed")
    stop_picom()
    DESKCTL_CONFIG.mkdir(parents=True, exist_ok=True)
    logfile = DESKCTL_CONFIG / "picom.log"
    with logfile.open("a") as log:
        log.write("\n--- deskctl compositor startup ---\n")
        log.flush()
        process = subprocess.Popen(
            ["picom", "--config", str(PICOM)], stdout=log, stderr=log,
            start_new_session=True,
        )
        try:
            code = process.wait(timeout=0.5)
        except subprocess.TimeoutExpired:
            return "picom running (startup checked)"
    raise RuntimeError(f"picom exited during startup ({code}); see {logfile}")


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as file:
        temporary = Path(file.name)
        try:
            file.write(text)
            file.flush()
            os.fsync(file.fileno())
            if path.exists():
                temporary.chmod(path.stat().st_mode & 0o777)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)


def on_off(enabled):
    return "ON" if enabled else "OFF"


def current_wallpaper_path():
    if not FEHBG.exists():
        return None
    for line in FEHBG.read_text().splitlines():
        line = line.strip()
        if line.startswith("feh ") and "--bg-" in line:
            try:
                return Path(shlex.split(line)[-1])
            except ValueError:
                return None
    return None


def cycle_wallpaper(state, direction):
    images = wallpaper_images()
    if not images:
        state["wallpaper"] = None
        return
    current = state.get("wallpaper") or current_wallpaper_path()
    try:
        idx = images.index(current)
    except ValueError:
        idx = 0
    state["wallpaper"] = images[(idx + direction) % len(images)]


def wallpaper_value(state):
    path = state.get("wallpaper") or current_wallpaper_path()
    return path.name if path else "unset"


def display_brightness():
    if not DISPLAY_BRIGHTNESS.exists():
        return "1.0"
    value = DISPLAY_BRIGHTNESS.read_text().strip()
    return value if value in BRIGHTNESS_VALUES else "1.0"


def connected_monitors():
    """Return active monitors in physical left-to-right order."""
    code, out = run(["xrandr", "--query"])
    if code != 0:
        raise RuntimeError(out or "xrandr failed")

    monitors = []
    geometry_re = re.compile(r"(\d+)x(\d+)([+-]\d+)([+-]\d+)")
    for line in out.splitlines():
        if not re.match(r"^\S+\s+connected(?:\s|$)", line):
            continue
        match = geometry_re.search(line)
        if not match:  # Connected but disabled outputs are not desktop monitors.
            continue
        width, height, x, y = map(int, match.groups())
        words = line.split()
        # A non-normal current rotation follows the geometry. The rotations in
        # parentheses are merely the output's supported rotations.
        after_geometry = line[match.end():].split()
        rotation = (
            after_geometry[0]
            if after_geometry and after_geometry[0] in ("normal", "left", "right", "inverted")
            else "normal"
        )
        portrait = rotation in ("left", "right")
        monitors.append({
            "output": words[0],
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "base_width": height if portrait else width,
            "base_height": width if portrait else height,
            "orientation": "portrait" if portrait else "landscape",
            "rotation": rotation,
        })
    monitors.sort(key=lambda monitor: (monitor["x"], monitor["y"], monitor["output"]))
    return monitors


def set_display_brightness(value):
    if not command_exists("xrandr"):
        raise RuntimeError("xrandr is not installed")

    outputs = [monitor["output"] for monitor in connected_monitors()]
    if not outputs:
        raise RuntimeError("no active xrandr outputs found")

    for output in outputs:
        code, out = run(["xrandr", "--output", output, "--brightness", value])
        if code != 0:
            raise RuntimeError(out or f"failed to dim {output}")

    DESKCTL_CONFIG.mkdir(parents=True, exist_ok=True)
    DISPLAY_BRIGHTNESS.write_text(value + "\n")


DESKCTL_LOGO = [
"   ██████╗ ███████╗███████╗██╗  ██╗████████╗ ██████╗ ██████╗  ",
"   ██╔══██╗██╔════╝██╔════╝██║ ██╔╝╚══██╔══╝██╔═══██╗██╔══██╗ ",
"   ██║  ██║█████╗  ███████╗█████╔╝    ██║   ██║   ██║██████╔╝ ",
"   ██║  ██║██╔══╝  ╚════██║██╔═██╗    ██║   ██║   ██║██╔═══╝  ",
"   ██████╔╝███████╗███████║██║  ██╗   ██║   ╚██████╔╝██║      ",
"   ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝      ",
"███╗   ███╗ █████╗ ███╗   ██╗ █████╗  ██████╗ ███████╗██████╗ ",
"████╗ ████║██╔══██╗████╗  ██║██╔══██╗██╔════╝ ██╔════╝██╔══██╗",
"██╔████╔██║███████║██╔██╗ ██║███████║██║  ███╗█████╗  ██████╔╝",
"██║╚██╔╝██║██╔══██║██║╚██╗██║██╔══██║██║   ██║██╔══╝  ██╔══██╗",
"██║ ╚═╝ ██║██║  ██║██║ ╚████║██║  ██║╚██████╔╝███████╗██║  ██║",
"╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝",
]


def draw_text(stdscr, y, x, text, width, attr=0):
    rows, columns = stdscr.getmaxyx()
    if not (0 <= y < rows and 0 <= x < columns):
        return
    width = min(width, columns - x - (y == rows - 1))
    if width > 0:
        try:
            stdscr.addnstr(y, x, text, width, attr)
        except curses.error:
            # A resize or a wide character can exhaust the available cells.
            pass


def draw_centered(stdscr, y, text, attr=0):
    _, w = stdscr.getmaxyx()
    x = max(0, (w - len(text)) // 2)
    draw_text(stdscr, y, x, text, max(0, w - x), attr)


def init_colors():
    curses.start_color()
    curses.use_default_colors()
    if hasattr(curses, "assume_default_colors"):
        curses.assume_default_colors(-1, -1)
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_RED, -1)
    curses.init_pair(3, curses.COLOR_CYAN, -1)


def set_title_color(hex_color):
    """Set pair 4 to the closest terminal color without recoloring other UI."""
    red, green, blue = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    if curses.COLORS >= 256:
        levels = [0, 95, 135, 175, 215, 255]
        parts = [min(range(6), key=lambda i: abs(levels[i] - value)) for value in (red, green, blue)]
        color = 16 + 36 * parts[0] + 6 * parts[1] + parts[2]
    else:
        color = max(
            range(8),
            key=lambda candidate: sum(
                component * expected
                for component, expected in zip(
                    (red, green, blue),
                    ((candidate & 1) > 0, (candidate & 2) > 0, (candidate & 4) > 0),
                )
            ),
        )
    curses.init_pair(4, color, -1)


def value_attr(value, selected=False):
    attr = curses.A_REVERSE if selected else 0
    if value == "ON":
        return attr | curses.color_pair(1) | curses.A_BOLD
    if value == "OFF":
        return attr | curses.color_pair(2) | curses.A_BOLD
    return attr


def initial_state():
    picom = read(PICOM)
    monitors = connected_monitors() if command_exists("xrandr") else []
    current_accent = accent_color()
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", current_accent):
        current_accent = ACCENT_COLORS[0][1]
    return {
        "blur": blur_enabled(picom),
        "shadow": get_picom_key(picom, "shadow", "false") == "true",
        "fading": get_picom_key(picom, "fading", "false") == "true",
        "vsync": get_picom_key(picom, "vsync", "true") == "true",
        "inactive_opacity": inactive_opacity(picom),
        "active_opacity": active_opacity(picom),
        "brightness": display_brightness(),
        "corner_radius": get_picom_key(picom, "corner-radius", "0"),
        "backend": get_picom_key(picom, "backend", BACKENDS[0]),
        "wallpaper": current_wallpaper_path(),
        "accent": current_accent,
        "monitors": monitors,
        "applied_monitor_layout": monitor_layout_signature(monitors),
    }


def cycle_state(state, key, values, direction, wrap=True):
    current = state[key]
    if wrap:
        state[key] = previous_value(current, values) if direction < 0 else next_value(current, values)
    else:
        state[key] = stepped_value(current, values, direction)


def monitor_layout_signature(monitors):
    return tuple((monitor["output"], monitor["orientation"]) for monitor in monitors)


def apply_monitor_layout(monitors):
    if not monitors:
        return None
    command = ["xrandr"]
    x = 0
    for monitor in monitors:
        portrait = monitor["orientation"] == "portrait"
        monitor_width = monitor["base_height"] if portrait else monitor["base_width"]
        monitor_height = monitor["base_width"] if portrait else monitor["base_height"]
        command.extend([
            "--output", monitor["output"],
            "--rotate", "right" if portrait else "normal",
            "--pos", f"{x}x0",
        ])
        monitor["pending_x"] = x
        monitor["pending_width"] = monitor_width
        monitor["pending_height"] = monitor_height
        x += monitor_width
    code, output = run(command)
    if code != 0:
        raise RuntimeError(output or "failed to apply monitor layout")
    for monitor in monitors:
        monitor["x"] = monitor.pop("pending_x")
        monitor["y"] = 0
        monitor["rotation"] = "right" if monitor["orientation"] == "portrait" else "normal"
        monitor["width"] = monitor.pop("pending_width")
        monitor["height"] = monitor.pop("pending_height")
    return "monitor layout applied"


def save_session_state(state):
    """Persist live-only settings so DWM startup can restore them."""
    DESKCTL_CONFIG.mkdir(parents=True, exist_ok=True)
    saved = {
        "accent": state["accent"],
        "monitors": [
            {
                "output": monitor["output"],
                "orientation": monitor["orientation"],
                "x": monitor["x"],
                "y": monitor["y"],
                "rotation": monitor["rotation"],
            }
            for monitor in state["monitors"]
        ],
    }
    atomic_write(SESSION_STATE, json.dumps(saved, indent=2) + "\n")


def restore_session_state():
    """Restore settings which do not live in ordinary application configs."""
    if not SESSION_STATE.exists():
        return
    try:
        saved = json.loads(SESSION_STATE.read_text())
        if not isinstance(saved, dict):
            raise ValueError("expected an object")
        accent = saved.get("accent")
        if accent is not None and (not isinstance(accent, str) or
                                   not re.fullmatch(r"#[0-9a-fA-F]{6}", accent)):
            raise ValueError("invalid accent")
        monitors = saved.get("monitors", [])
        if not isinstance(monitors, list) or any(
            not isinstance(item, dict) or
            not isinstance(item.get("output"), str) or not item["output"] or
            item.get("orientation") not in ("landscape", "portrait")
            for item in monitors
        ):
            raise ValueError("invalid monitor list")
    except (OSError, ValueError) as error:
        print(f"Skipping invalid deskctl session state: {error}", file=sys.stderr)
        return

    accent = saved.get("accent")
    if accent and re.fullmatch(r"#[0-9a-fA-F]{6}", accent):
        set_mc_accent(accent)
    if accent and re.fullmatch(r"#[0-9a-fA-F]{6}", accent) and command_exists("xprop"):
        run(["xprop", "-root", "-f", DWM_ACCENT_PROPERTY, "8s", "-set", DWM_ACCENT_PROPERTY, accent])

    if not saved.get("monitors") or not command_exists("xrandr"):
        return
    # Old saves lack exact geometry; leave the current arrangement untouched.
    if any(type(item.get("x")) is not int or type(item.get("y")) is not int or
           item.get("rotation") not in ("normal", "left", "right", "inverted")
           for item in monitors):
        print("Skipping saved monitor layout without valid positions/rotations; "
              "apply settings once to save the current layout.", file=sys.stderr)
        return
    active = {monitor["output"] for monitor in connected_monitors()}
    command = ["xrandr"]
    for item in monitors:
        if item["output"] in active:
            command.extend([
                "--output", item["output"], "--rotate", item["rotation"],
                "--pos", f"{item['x']}x{item['y']}",
            ])
    if len(command) > 1:
        code, output = run(command)
        if code != 0:
            raise RuntimeError(output or "failed to restore monitor layout")


def apply_settings(state):
    previous = read(PICOM)
    text = previous
    text = remove_block(text, "blur")
    text = set_picom_key(text, "blur-background", "true" if state["blur"] else "false")
    if state["blur"]:
        text = set_picom_key(text, "blur-method", '"dual_kawase"')
        text = set_picom_key(text, "blur-strength", "4")
    for key in ("shadow", "fading", "vsync"):
        text = set_picom_key(text, key, "true" if state[key] else "false")
    # Bundled window rules inherit the switches instead of forcing effects on.
    for match in ("class_g = 'st-256color'", "window_type = 'dock'", "class_g = 'slop'"):
        for key in ("shadow", "fade", "blur-background"):
            text = remove_rule_property(text, match, key)
    text = set_picom_key(text, "no-fading-openclose", "false" if state["fading"] else "true")
    if state["shadow"]:
        for key, value in (("shadow-radius", "14"), ("shadow-offset-x", "-10"),
                           ("shadow-offset-y", "-10"), ("shadow-opacity", "0.32")):
            text = set_picom_key(text, key, value)
    if state["fading"]:
        for key, value in (("fade-delta", "8"), ("fade-in-step", "0.06"),
                           ("fade-out-step", "0.06")):
            text = set_picom_key(text, key, value)
    text = remove_picom_key(text, "inactive-opacity")
    text = remove_picom_key(text, "active-opacity")
    text = remove_rule_property(text, "!focused", "opacity")
    text = remove_empty_rule(text, "!focused")
    text = set_rule_property(text, "!focused && !group_focused", "opacity", state["inactive_opacity"])
    text = set_rule_property(text, "focused || group_focused", "opacity", state["active_opacity"])
    text = set_picom_key(text, "corner-radius", state["corner_radius"])
    text = remove_picom_list_item(text, "rounded-corners-exclude", "window_type = 'dock'")
    text = remove_rule_property(text, "class_g = 'st-256color'", "corner-radius")
    text = set_rule_property(text, "window_type = 'dock'", "corner-radius", state["corner_radius"])
    text = set_picom_key(text, "backend", state["backend"])
    atomic_write(PICOM, text)
    try:
        messages = [sync_picom()]
    except Exception as error:
        atomic_write(PICOM, previous)
        try:
            sync_picom()
        except Exception as recovery:
            raise RuntimeError(f"{error}; previous config restored, but restart failed: {recovery}") from error
        raise RuntimeError(f"{error}; previous compositor configuration restored") from error
    try:
        set_display_brightness(state["brightness"])
        messages.append(f"brightness {state['brightness']}")
        if state.get("wallpaper") and state["wallpaper"] != current_wallpaper_path():
            messages.append(set_wallpaper(state["wallpaper"]))
        if state["accent"].lower() != accent_color().lower():
            messages.append(set_accent_color(state["accent"]))
        else:
            set_mc_accent(state["accent"])
        signature = monitor_layout_signature(state["monitors"])
        if signature != state["applied_monitor_layout"]:
            messages.append(apply_monitor_layout(state["monitors"]))
            state["applied_monitor_layout"] = signature
        save_session_state(state)
    except Exception as error:
        raise RuntimeError(f"Partly applied: {' | '.join(messages)}; stopped: {error}") from error
    return " | ".join(messages)


def settings_items(state):
    items = [
        {
            "name": "BLUR",
            "value": lambda: on_off(state["blur"]),
            "change": lambda direction: state.update(blur=not state["blur"]),
        },
        {
            "name": "SHADOWS",
            "value": lambda: on_off(state["shadow"]),
            "change": lambda direction: state.update(shadow=not state["shadow"]),
        },
        {
            "name": "POPUP FADE",
            "value": lambda: on_off(state["fading"]),
            "change": lambda direction: state.update(fading=not state["fading"]),
        },
        {
            "name": "VSYNC",
            "value": lambda: on_off(state["vsync"]),
            "change": lambda direction: state.update(vsync=not state["vsync"]),
        },
        {
            "name": "INACTIVE OPACITY",
            "value": lambda: state["inactive_opacity"],
            "change": lambda direction: cycle_state(state, "inactive_opacity", OPACITY_VALUES, direction),
        },
        {
            "name": "ACTIVE OPACITY",
            "value": lambda: state["active_opacity"],
            "change": lambda direction: cycle_state(state, "active_opacity", OPACITY_VALUES, direction),
        },
        {
            "name": "SCREEN DIMMER",
            "value": lambda: state["brightness"],
            "change": lambda direction: cycle_state(state, "brightness", BRIGHTNESS_VALUES, direction, False),
        },
        {
            "name": "CORNER RADIUS",
            "value": lambda: state["corner_radius"],
            "change": lambda direction: cycle_state(state, "corner_radius", CORNER_RADII, direction),
        },
        {
            "name": "BACKEND RENDERING",
            "value": lambda: state["backend"].strip('"'),
            "change": lambda direction: cycle_state(state, "backend", BACKENDS, direction),
        },
        {
            "name": "WALLPAPER",
            "value": lambda: wallpaper_value(state),
            "change": lambda direction: cycle_wallpaper(state, direction),
        },
        {
            "name": "DWM / DMENU COLOR",
            "value": lambda: next((f"{name} ({color})" for name, color in ACCENT_COLORS
                                   if color.lower() == state["accent"].lower()), f"CUSTOM ({state['accent']})"),
            "change": lambda direction: cycle_state(state, "accent", tuple(color for _, color in ACCENT_COLORS), direction),
            "choose": True,
        },
    ]
    for monitor in state["monitors"]:
        items.append({
            "name": f"MONITOR {state['monitors'].index(monitor) + 1}",
            "value": lambda monitor=monitor: monitor["output"],
            "monitor": monitor,
        })
    items.extend([
        {
            "name": "APPLY SETTINGS",
            "value": lambda: "Press Enter To Apply Settings",
            "apply": lambda: apply_settings(state),
        },
        {
            "name": "EXIT",
            "value": lambda: "Press Enter To Exit",
            "exit": True,
        },
    ])
    return items


def draw_settings(stdscr, items, idx, status, state):
    h, w = stdscr.getmaxyx()
    stdscr.erase()
    set_title_color(state["accent"])
    if h < 9 or w < 20:
        logo_fits = w >= max(map(len, DESKCTL_LOGO)) and h >= len(DESKCTL_LOGO) + 5
        if logo_fits:
            for line_no, line in enumerate(DESKCTL_LOGO):
                draw_centered(stdscr, line_no, line, curses.color_pair(4) | curses.A_BOLD)
            header_y = len(DESKCTL_LOGO) + 1
        else:
            draw_text(stdscr, 0, 1, "deskctl manager", max(0, w - 2), curses.color_pair(4) | curses.A_BOLD)
            header_y = 1

        draw_text(stdscr, header_y, 1, "Use Up/Down, Left/Right, Enter Apply/Exit", max(0, w - 2), curses.A_DIM)
        visible_rows = max(1, h - header_y - 3)
        first_item = max(0, min(idx - visible_rows // 2, len(items) - visible_rows))
        visible_items = items[first_item:first_item + visible_rows]
        for row, item in enumerate(visible_items, header_y + 2):
            selected = first_item + row - (header_y + 2) == idx
            value = str(item["value"]())
            attr = curses.A_REVERSE if selected else 0
            draw_text(stdscr, row, 1, f"{item['name']}: {value}", max(0, w - 2), attr)
        draw_text(stdscr, h - 1, 1, status, max(0, w - 2), curses.A_DIM)
        stdscr.refresh()
        return

    logo_fits = w >= max(map(len, DESKCTL_LOGO)) and h >= len(DESKCTL_LOGO) + 9
    if logo_fits:
        for line_no, line in enumerate(DESKCTL_LOGO):
            draw_centered(stdscr, line_no, line, curses.color_pair(4) | curses.A_BOLD)
        y = len(DESKCTL_LOGO) + 1
    else:
        draw_centered(stdscr, 0, "deskctl manager", curses.A_BOLD)
        y = 2

    table_w = min(75, w - 2)
    left_w = min(25, (table_w - 3) // 2)
    right_w = table_w - left_w - 3
    x = max(0, (w - table_w) // 2)
    draw_text(stdscr, y, x, "┌" + "─" * left_w + "┬" + "─" * right_w + "┐", table_w)
    draw_text(stdscr, y + 1, x, "│" + "OPTION".center(left_w) + "│" + "VALUE".center(right_w) + "│", table_w, curses.A_BOLD)
    draw_text(stdscr, y + 2, x, "├" + "─" * left_w + "┼" + "─" * right_w + "┤", table_w)
    row_y = y + 3
    visible_rows = max(1, (h - y - 6) // 2)
    first_item = max(0, min(idx - visible_rows // 2, len(items) - visible_rows))
    visible_items = items[first_item:first_item + visible_rows]
    for i, item in enumerate(visible_items):
        selected = first_item + i == idx
        value = str(item["value"]())
        row_attr = curses.A_REVERSE if selected else 0
        draw_text(stdscr, row_y, x, "│", 1, row_attr)
        draw_text(stdscr, row_y, x + 1, item["name"].ljust(left_w), left_w, row_attr)
        draw_text(stdscr, row_y, x + 1 + left_w, "│", 1, row_attr)
        draw_text(stdscr, row_y, x + 2 + left_w, value[:right_w].ljust(right_w), right_w, value_attr(value, selected))
        draw_text(stdscr, row_y, x + table_w - 1, "│", 1, row_attr)
        row_y += 1
        sep = "└" if i == len(visible_items) - 1 else "├"
        mid = "┴" if i == len(visible_items) - 1 else "┼"
        end = "┘" if i == len(visible_items) - 1 else "┤"
        draw_text(stdscr, row_y, x, sep + "─" * left_w + mid + "─" * right_w + end, table_w)
        row_y += 1

    nav = "Navigation: Up/Down select  Left/Right cycle  Enter apply/exit  q exit"
    if len(visible_items) < len(items):
        nav = f"{first_item + 1}-{first_item + len(visible_items)}/{len(items)}  " + nav
    draw_centered(stdscr, min(row_y + 1, h - 2), nav, curses.A_DIM)
    if status:
        draw_centered(stdscr, h - 1, status.replace("\n", " | "), curses.A_DIM)
    stdscr.refresh()


def choose_accent_color(stdscr, state):
    current = state["accent"].lower()
    idx = next(
        (i for i, (_, color) in enumerate(ACCENT_COLORS) if color.lower() == current),
        0,
    )

    while True:
        h, w = stdscr.getmaxyx()
        stdscr.erase()
        draw_centered(stdscr, 1, "Choose DWM / dmenu color", curses.A_BOLD)
        start_y = max(3, (h - len(ACCENT_COLORS)) // 2)
        for i, (name, color) in enumerate(ACCENT_COLORS):
            label = f"{name:<8} {color}"
            attr = curses.A_REVERSE | curses.A_BOLD if i == idx else 0
            draw_centered(stdscr, start_y + i, label, attr)
        draw_centered(stdscr, min(h - 1, start_y + len(ACCENT_COLORS) + 1), "Up/Down select  Enter apply  Esc cancel", curses.A_DIM)
        stdscr.refresh()

        key = stdscr.getch()
        if key in (27, ord("q")):
            return None
        if key == curses.KEY_DOWN:
            idx = (idx + 1) % len(ACCENT_COLORS)
        elif key == curses.KEY_UP:
            idx = (idx - 1) % len(ACCENT_COLORS)
        elif key in (10, 13, curses.KEY_ENTER):
            name, color = ACCENT_COLORS[idx]
            state["accent"] = color
            return f"DWM / DMENU COLOR staged: {name} ({color})"


def identify_monitor(monitor):
    output = monitor["output"]
    code, message = run(["xrandr", "--output", output, "--brightness", "0.20"])
    if code != 0:
        return f"error: {message or f'could not identify {output}'}"

    applied_brightness = display_brightness()

    def restore():
        run(["xrandr", "--output", output, "--brightness", applied_brightness])

    timer = threading.Timer(0.7, restore)
    # Finish restoring brightness even if the settings window closes meanwhile.
    timer.daemon = False
    timer.start()
    return f"identifying {output} with a brief dim pulse"


def move_monitor(monitors, monitor, direction):
    index = monitors.index(monitor)
    destination = max(0, min(len(monitors) - 1, index + direction))
    if destination != index:
        monitors.pop(index)
        monitors.insert(destination, monitor)


def edit_monitor(stdscr, state, monitor):
    idx = 0
    status = "Changes are staged until APPLY SETTINGS"
    while True:
        monitors = state["monitors"]
        position = monitors.index(monitor) + 1
        rows = [
            ("ORIENTATION LANDSCAPE", on_off(monitor["orientation"] == "landscape")),
            ("ORIENTATION PORTRAIT", on_off(monitor["orientation"] == "portrait")),
            ("IDENTIFY MONITOR", "Press Enter To Identify"),
            ("MONITOR POSITION", f"Position {position} from {len(monitors)}"),
        ]
        h, w = stdscr.getmaxyx()
        stdscr.erase()
        draw_centered(stdscr, 1, f"MONITOR {position}: {monitor['output']}", curses.A_BOLD)
        start = max(3, (h - len(rows) * 2) // 2)
        for row_idx, (name, value) in enumerate(rows):
            attr = curses.A_REVERSE if row_idx == idx else 0
            draw_centered(stdscr, start + row_idx * 2, f"{name:<24} {value}", value_attr(value, row_idx == idx) or attr)
        draw_centered(stdscr, min(h - 1, start + len(rows) * 2 + 1),
                      "Up/Down select  Left/Right change  Enter select/identify  Esc back", curses.A_DIM)
        if status:
            draw_centered(stdscr, h - 1, status, curses.A_DIM)
        stdscr.refresh()
        key = stdscr.getch()
        if key in (27, ord("q")):
            return status
        if key == curses.KEY_DOWN:
            idx = (idx + 1) % len(rows)
        elif key == curses.KEY_UP:
            idx = (idx - 1) % len(rows)
        elif key in (curses.KEY_LEFT, curses.KEY_RIGHT):
            direction = -1 if key == curses.KEY_LEFT else 1
            if idx == 0:
                monitor["orientation"] = "landscape"
                status = "landscape staged"
            elif idx == 1:
                monitor["orientation"] = "portrait"
                status = "portrait staged"
            elif idx == 3:
                move_monitor(monitors, monitor, direction)
                status = f"position {monitors.index(monitor) + 1} staged"
        elif key in (10, 13, curses.KEY_ENTER):
            if idx == 0:
                monitor["orientation"] = "landscape"
                status = "landscape staged"
            elif idx == 1:
                monitor["orientation"] = "portrait"
                status = "portrait staged"
            elif idx == 2:
                status = identify_monitor(monitor)


def main(stdscr):
    curses.curs_set(0)
    init_colors()
    state = initial_state()
    idx = 0
    status = ""

    while True:
        items = settings_items(state)
        idx = min(idx, len(items) - 1)
        draw_settings(stdscr, items, idx, status, state)
        key = stdscr.getch()
        if key in (ord("q"), 27):
            return
        if key == curses.KEY_DOWN:
            idx = (idx + 1) % len(items)
        elif key == curses.KEY_UP:
            idx = (idx - 1) % len(items)
        elif key in (curses.KEY_LEFT, curses.KEY_RIGHT):
            item = items[idx]
            if item.get("monitor"):
                try:
                    status = edit_monitor(stdscr, state, item["monitor"])
                except Exception as exc:
                    status = f"error: {exc}"
            elif "change" in item:
                direction = -1 if key == curses.KEY_LEFT else 1
                try:
                    item["change"](direction)
                    status = f"{item['name']} = {item['value']()}"
                except Exception as exc:
                    status = f"error: {exc}"
        elif key in (10, 13, curses.KEY_ENTER):
            item = items[idx]
            if item.get("exit"):
                return
            if item.get("choose"):
                try:
                    result = choose_accent_color(stdscr, state)
                    if result is not None:
                        status = result
                except Exception as exc:
                    status = f"error: {exc}"
            elif item.get("monitor"):
                try:
                    status = edit_monitor(stdscr, state, item["monitor"])
                except Exception as exc:
                    status = f"error: {exc}"
            elif "apply" in item:
                try:
                    status = item["apply"]()
                except Exception as exc:
                    status = f"error: {exc}"


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--restore-session":
        restore_session_state()
    elif len(sys.argv) > 1 and sys.argv[1] == "--sync-compositor":
        try:
            print(sync_picom())
        except Exception as error:
            print(f"deskctl: {error}", file=sys.stderr)
            sys.exit(1)
    else:
        curses.wrapper(main)
