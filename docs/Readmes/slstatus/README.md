# Slstatus

Supplies the system information shown in DWM's status bar. The [session launcher](../../../config/dwm/start-dwm.sh) starts it automatically.

## Displayed information

The configuration refreshes every three seconds and includes:

- Default PipeWire output volume and mute state, read through `wpctl` once at startup and cached until a DWM volume or output-mute key triggers a refresh.
- Package updates, with a check interval of 1,800 seconds.
- Download and upload rates, with shared automatic network interface selection per refresh on Linux and rates based on actual elapsed time.
- Used memory and CPU usage.
- Battery percentage when a battery is available, checked once a minute.
- Date and time.

Unavailable values generally display as `n/a`. A Nerd Font is needed for the configured icons.

The DWM volume keys send `SIGUSR1` to the current user's Slstatus processes after a successful audio change. Changes made through another mixer or by switching output devices are reflected on the next key-triggered refresh. To refresh manually, run:

```sh
pkill -USR1 -u "$(id -u)" -x slstatus
```

The battery cache also remembers when no battery is present. Adding or removing a battery can take up to a minute to appear, plus the normal status refresh delay.

## Configuration and building

Edit [config.h](../../../config/slstatus/config.h) to change the refresh interval, output formats, or the `args` array of status components. Component implementations are in [components/](../../../config/slstatus/components); compiler and linker settings are in [config.mk](../../../config/slstatus/config.mk).

The [installer](../installer/README.md) builds and deploys this program. Building requires a C compiler, Make, and Xlib. After editing the installed configuration:

```sh
make -C ~/.config/slstatus
```

Start a new DWM session to use the rebuilt status process. For a one-shot preview in a terminal:

```sh
~/.config/slstatus/slstatus -s -1
```

[Back to documentation](../../../README.md#documentation)

[Documentation index](../../../README.md#documentation)
