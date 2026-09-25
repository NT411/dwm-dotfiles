#!/bin/sh

mon="${1:-0}"

monitor_geometry() {
    xrandr --current | awk -v mon="$mon" '
    / connected/ {
        geom = ""
        for (i = 3; i <= NF; i++) {
            if ($i ~ /^[0-9]+x[0-9]+[+-][0-9]+[+-][0-9]+/) {
                geom = $i
                break
            }
        }

        if (geom != "") {
            if (seen == mon) {
                gsub(/[+-]/, " &", geom)
                split(geom, pos, /[x ]/)
                print pos[3], pos[4], pos[1], pos[2]
                exit
            }
            seen++
        }
    }'
}

dwm_bar_geometry() {
    set -- $(monitor_geometry)
    [ "$#" -eq 4 ] || return 1

    mon_x="$1"
    mon_y="$2"
    mon_w="$3"
    mon_h="$4"

    xwininfo -root -children 2>/dev/null | awk \
        -v mx="$mon_x" -v my="$mon_y" -v mw="$mon_w" -v mh="$mon_h" '
    /\("dwm" "dwm"\)/ {
        if (match($0, /[0-9]+x[0-9]+[+-][0-9]+[+-][0-9]+/)) {
            geom = substr($0, RSTART, RLENGTH)
            gsub(/[+-]/, " &", geom)
            split(geom, parts, /[x ]/)
            width = parts[1]
            height = parts[2]
            x = parts[3]
            y = parts[4]

            if (x >= mx && x < mx + mw && y >= my && y < my + mh) {
                print x - mx, y - my, width, height
                exit
            }
        }
    }'
}

set -- $(dwm_bar_geometry)

if [ "$#" -eq 4 ]; then
    exec dmenu_run \
        -m "$mon" \
        -x "$1" -y "$2" \
        -z "$3" -h "$4" \
        -fn 'JetBrainsMono Nerd Font:size=12' \
        -nb '#1e1e2e' -nf '#cdd6f4' \
        -sb '#ffffff' -sf '#11111b'
fi

set -- $(monitor_geometry)
mon_w="${3:-}"

[ -n "$mon_w" ] || mon_w=$(xdpyinfo | awk '/dimensions:/ {split($2, a, "x"); print a[1]; exit}')

exec dmenu_run \
    -m "$mon" \
    -x 10 -y 10 \
    -z "$((mon_w - 20))" \
    -fn 'JetBrainsMono Nerd Font:size=12' \
    -nb '#1e1e2e' -nf '#cdd6f4' \
    -sb '#ffffff' -sf '#11111b'
