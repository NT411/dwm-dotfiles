#!/bin/sh

# Set up the graphical environment for user services and D-Bus activation.
if [ -d /etc/X11/xinit/xinitrc.d ]; then
    for hook in /etc/X11/xinit/xinitrc.d/?*.sh; do
        [ -x "$hook" ] && . "$hook"
    done
    unset hook
fi

exec "$HOME/.config/dwm/start-dwm.sh"
