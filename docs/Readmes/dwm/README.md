# DWM

The X11 window manager for this desktop. This build uses five tags, a top bar, configurable gaps, and `###` (nrowgrid) as the default layout. The other layouts are `HHH` (grid), `TTT` (bottom stack), `:::` (gapless grid), and `---` (horizontal grid).

There are five layouts total: four grids and bottom stack. Cycling follows
`###` → `HHH` → `TTT` → `:::` → `---`, then wraps around. Click the layout
symbol with the left mouse button or scroll down to advance; right-click or
scroll up to go back. All five layouts support the configured gaps.

## Configuration

- [config.h](../../../config/dwm/config.h): colors, fonts, tags, application commands, layouts, and keybindings.
- [config.mk](../../../config/dwm/config.mk): compiler flags, libraries, and installation paths.
- [start-dwm.sh](../../../config/dwm/start-dwm.sh): restores desktop settings and wallpaper, starts Slstatus and Picom, then launches DWM. Set `DWM_COMPOSITOR=0` to skip starting Picom.

The configured font is JetBrainsMono Nerd Font. Build dependencies include a C compiler, Make, Xlib, Xinerama, Xft, and Fontconfig.

## Usage

After using the [installer](../installer/README.md), run `startx` from a TTY or select **DWM (local dotfiles)** in a display manager.

| Shortcut | Action |
| --- | --- |
| Super + Enter | Open ST |
| Super + P | Open Dmenu |
| Super + D | Open the desktop manager |
| Super + 1–5 | Select a tag |
| Super + Shift + 1–5 | Move the focused window to a tag |
| Super + Left / Right | Move focus; cross tags at window-list boundaries and monitors at tag boundaries |
| Super + Alt + Left / Right | Reorder the focused window; move it across tags and monitors at boundaries |
| Super + [ / ] | Cycle layouts |
| Super + Shift + T / Y / M | Select nrowgrid / grid / bottom stack |
| Super + Alt + U | Increase gaps |
| Super + Alt + Shift + U | Decrease gaps |
| Super + Alt + 0 | Toggle gaps |
| Super + Shift + B | Toggle the bar |
| Super + Alt + Q | Quit DWM |

## Rebuilding

The installer runs the binary in `~/.config/dwm`. After editing its `config.h`, rebuild it with:

```sh
make -C ~/.config/dwm
```

Log out of DWM and start a new session to load the rebuilt binary. Changes made only in this repository must be deployed before they affect the installed desktop.

[Back to documentation](../../../README.md#documentation)

[Documentation index](../../../README.md#documentation)
