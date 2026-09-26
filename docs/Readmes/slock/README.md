# Slock

The X11 screen locker opened with **Super + L** in DWM. You can also run `slock` from a terminal. Type your login password and press Enter to unlock.

## Configuration

[config.h](../../../config/slock/config.h) controls the initial, typing, and failure colors and the lock window opacity, currently `0.5`. The lock screen displays no message and does not load a text font. The configured privilege-drop user and group are both `nobody`.

This fork uses a translucent lock window; compositing and blur depend on the active Picom configuration. See [the Picom configuration](../../../config/picom/picom.conf).

## Building and installation

Build dependencies include a C compiler, Make, Xlib, Xext, Xrandr, and libcrypt. [config.mk](../../../config/slock/config.mk) contains the build settings.

The [installer](../installer/README.md) builds Slock and installs a root-owned, setuid executable at `/usr/local/bin/slock`, with a link in `~/.local/bin`. After editing the installed source, rebuild and replace that executable:

```sh
make -C ~/.config/slock
sudo install -o root -g root -m 4755 ~/.config/slock/slock /usr/local/bin/slock
```

Rebuilding the user-owned source alone does not update the installed locker.

[Back to documentation](../../../README.md#documentation)

[Documentation index](../../../README.md#documentation)
