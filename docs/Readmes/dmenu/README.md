# Dmenu

The application launcher opened with **Super + P** in DWM.

## Configuration

- [config.h](../../../config/dmenu/config.h): default font, colors, position, and list size.
- [dmenu-launcher.sh](../../../config/dmenu/dmenu-launcher.sh): launcher appearance and positioning. It tries to match the DWM bar geometry and otherwise uses an inset at the top of the monitor.
- [config.mk](../../../config/dmenu/config.mk): build options and installation paths.

The launcher supplies font and color arguments that override the defaults in `config.h`. Edit the launcher to change the appearance seen with Super + P. This build supports custom geometry through `-x`, `-y`, `-z`, and `-h`.

## Usage and building

The [installer](../installer/README.md) builds Dmenu and links its commands into `~/.local/bin`. It requires a C compiler, Make, Xlib, Xinerama, Xft, and Fontconfig. The launcher also uses `xrandr`, `xwininfo`, and `xdpyinfo`.

After changing the installed `config.h`:

```sh
make -C ~/.config/dmenu
```

Launcher script edits take effect on the next launch without a rebuild. Run `dmenu_run` for the basic application menu, or pass a list to Dmenu directly:

```sh
printf '%s\n' first second third | dmenu -p 'Choose:'
```

[Back to documentation](../../../README.md#documentation)

[Documentation index](../../../README.md#documentation)
