#!/bin/sh

export PATH="$HOME/.local/bin:$HOME/.config/st:$HOME/.config/dmenu:$PATH"
export GTK_THEME=Adwaita:dark
export XCURSOR_THEME=Adwaita
export XCURSOR_SIZE=24

# Match the local dconf interface preferences (also used by GTK portal apps).
if command -v gsettings >/dev/null 2>&1; then
    gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'
    gsettings set org.gnome.desktop.interface gtk-theme 'Adwaita-dark'
    gsettings set org.gnome.desktop.interface icon-theme 'Adwaita'
    gsettings set org.gnome.desktop.interface cursor-theme 'Adwaita'
fi

# Restore deskctl settings that are otherwise only held by the X server.
if [ -x "$HOME/.config/scripts/deskctl.py" ]; then
    "$HOME/.config/scripts/deskctl.py" --restore-session
fi

if [ -x "$HOME/.fehbg" ]; then
    "$HOME/.fehbg"
elif [ -f "$HOME/Images/Wallpapers/wp2.png" ]; then
    feh --bg-scale "$HOME/Images/Wallpapers/wp2.png"
else
    xsetroot -solid '#1e1e2e'
fi

if command -v xrandr >/dev/null 2>&1 && [ -r "$HOME/.config/deskctl/display-brightness" ]; then
    deskctl_brightness=$(cat "$HOME/.config/deskctl/display-brightness")
    case "$deskctl_brightness" in
        0.35|0.45|0.55|0.65|0.75|0.85|1.0)
            xrandr --query | awk '/ connected/{print $1}' | while read -r deskctl_output; do
                xrandr --output "$deskctl_output" --brightness "$deskctl_brightness"
            done
            ;;
    esac
fi

"$HOME/.config/slstatus/slstatus" &

if [ "${DWM_COMPOSITOR:-1}" = "1" ] && command -v picom >/dev/null 2>&1; then
    "$HOME/.config/scripts/deskctl.py" --sync-compositor &
fi

exec "$HOME/.config/dwm/dwm"
