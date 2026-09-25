# Qutebrowser

![qutebrowser screenshot](../../Images/qutebrowser/qutebrowser.jpg)

This configuration provides a dark browser interface and a local start page with a clock, bookmarks, search shortcuts, and the wallpaper and accent color selected through deskctl.

## Files

| File | Purpose |
|:-----|:--------|
| [config.py](../../../config/qutebrowser/config.py) | Startup page, blocking lists, privacy settings, and browser colors |
| [startpage/index.html](../../../config/qutebrowser/startpage/index.html) | Start-page layout |
| [startpage/style.css](../../../config/qutebrowser/startpage/style.css) | Start-page appearance |
| [startpage/script.js](../../../config/qutebrowser/startpage/script.js) | Clock, bookmarks, search, and deskctl integration |

## Setup

The repository installer includes `qutebrowser`, `python-adblock`, and `pdfjs`. Install the configuration at `~/.config/qutebrowser/`, preserving the `startpage/` directory. The configured startup and default page is `~/.config/qutebrowser/startpage/index.html`.

Launch qutebrowser with **Super + B** in this DWM setup. Update the configured blocking lists from the browser command line:

```text
:adblock-update
```

Settings are maintained in `config.py`; loading the generated autoconfiguration is disabled by `config.load_autoconfig(False)`.

## Keybindings

This configuration uses qutebrowser's default keybindings. The shortcuts below apply in normal mode; press **Escape** to leave insert or hint mode. Keys are case-sensitive: `J` means **Shift + J**, while `gg` means press **g** twice.

| Key | Action |
|:----|:-------|
| **Super + B** | Launch qutebrowser from DWM |
| `o` / `O` | Enter a URL or search in the current tab / a new tab |
| `go` | Edit the current URL |
| `f` / `F` | Follow a link using hints in the current tab / a new tab |
| `h` / `j` / `k` / `l` | Scroll left / down / up / right |
| **Ctrl + D** / **Ctrl + U** | Scroll half a page down / up |
| `gg` / `G` | Jump to the top / bottom of the page |
| `H` / `L` | Go back / forward in history |
| `r` / `R` | Reload / reload bypassing the cache |
| `J` / `K` | Switch to the next / previous tab |
| `d` / `u` | Close the current tab / restore the last closed tab |
| **Ctrl + T** | Open the configured start page in a new tab |
| `/` | Search within the page |
| `n` / `N` | Jump to the next / previous search match |
| `yy` | Copy the current URL |
| `pp` / `Pp` | Open the clipboard contents in the current tab / a new tab |
| `M` | Bookmark the current page |
| `gb` / `gB` | Load a bookmark in the current tab / a new tab |
| `m` | Save a named quickmark |
| `b` / `B` | Load a quickmark in the current tab / a new tab |
| `i` | Enter insert mode to type into the page |
| `+` / `-` / `=` | Zoom in / zoom out / reset zoom |
| **F11** | Toggle fullscreen |
| `:` | Open the browser command line |
| `ZZ` | Save the session and quit |

Run `:help bindings.default` for the full default binding list.

## Start page

- Displays the local time and date, updating at each minute boundary while visible.
- Reads bookmarks from `~/.config/qutebrowser/bookmarks/urls`. Add a bookmark using `:bookmark-add`; the page checks for changes every two seconds while visible and when it regains focus or becomes visible.
- Reads the wallpaper path from `~/.fehbg`, using the `feh --no-fehbg --bg-…` command format written by deskctl. It reads the file without executing it.
- Reads the applied accent color from `~/.config/deskctl/session-state.json`. Wallpaper and accent changes are checked every two seconds while visible and on return to the page.

Hidden start-page tabs stop their clock and file-refresh timers. Returning to a tab refreshes it immediately and restarts the timers. Requests already in flight may finish after the tab is hidden.

Keep the installed directory layout so these relative file paths resolve correctly. The page loads Syne and DM Mono fonts from Google Fonts.

## Search shortcuts

Enter a query in the start-page search box and press **Enter**. Ordinary queries use DuckDuckGo; domain-like input such as `example.com` opens with HTTPS.

## Browser settings

The configuration enables both adblock and hosts-based blocking, using EasyList, EasyPrivacy, uBlock's badware list, and StevenBlack's hosts list.

Third-party cookies, notifications, autoplay, DNS prefetching, and hyperlink auditing are disabled. Location, microphone, camera, and JavaScript clipboard access ask for permission. WebRTC is configured to disable non-proxied UDP; canvas reading and WebGL remain enabled.

The browser requests dark website colors and enables forced dark mode with smart image handling. Browser interface colors are defined in `config.py`; the start page uses `startpage/style.css` and the applied deskctl accent.

[Back to the main README](../../../README.md)

[Documentation index](../../../README.md#documentation)
