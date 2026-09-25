# ~/.bashrc

export LS_COLORS="di=38;5;111:fi=38;5;252:ln=38;5;218:ex=38;5;151"

alias grep='grep --color=auto'

# ╔══════════════════════════════════════════════════════════════╗
# ║                           PROMPT                             ║
# ╚══════════════════════════════════════════════════════════════╝

__prompt_git_branch() {
    git rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
        PS1_GIT_BRANCH=""
        return
    }

    PS1_GIT_BRANCH=$(git branch --show-current 2>/dev/null)
}

PROMPT_COMMAND='__prompt_git_branch'
PS1='
 \[\e[38;5;189;1m\]Env:\[\e[38;5;183m\]${OSTYPE^^}\[\e[0m\]
 \[\e[38;5;189;1m\]Date:\[\e[38;5;217m\]\d\[\e[0m\]
 \[\e[38;5;189;1m\]Time:\[\e[38;5;151m\]\t\[\e[0m\]
 \[\e[38;5;189;1m\]User:\[\e[38;5;223m\]\u\[\e[0m\]
 \[\e[38;5;189;1m\]Branch:\[\e[38;5;218m\]${PS1_GIT_BRANCH}\[\e[0m\]
 \[\e[38;5;189;1m\]Folder:\[\e[38;5;159m\]\w\[\e[0m\]

 \[\e[38;5;225;1m\]\$\[\e[0m\] '
# ╔══════════════════════════════════════════════════════════════╗
# ║                         HISTORY                              ║
# ╚══════════════════════════════════════════════════════════════╝
HISTSIZE=1000
HISTFILESIZE=2000
HISTCONTROL=ignoredups:erasedups
# ╔══════════════════════════════════════════════════════════════╗
# ║                      SHELL OPTIONS                           ║
# ╚══════════════════════════════════════════════════════════════╝
shopt -s autocd
# ╔══════════════════════════════════════════════════════════════╗
# ║                     DIRECTORY SHORTCUTS                      ║
# ╚══════════════════════════════════════════════════════════════╝
alias .='cd ..'
alias md='mkdir -p'
alias cbash='micro ~/.bashrc'
alias cdwm='cd ~/.config/dwm/'
alias cslstatus='micro ~/.config/slstatus/config.h'
# ╔══════════════════════════════════════════════════════════════╗
# ║                      SYSTEM COMMANDS                         ║
# ╚══════════════════════════════════════════════════════════════╝
alias c='clear'
alias l='ls'
alias ls='ls -a -F -v --color'
alias ll='ls -1 --color'
alias off='poweroff'
alias del='sudo rm -rf'
# ╔══════════════════════════════════════════════════════════════╗
# ║                    PACKAGE MANAGEMENT                        ║
# ╚══════════════════════════════════════════════════════════════╝
alias update='sudo pacman -Syu'
alias cache='sudo du -sh /var/cache/pacman/pkg'
alias delcache='sudo rm -rf /var/cache/pacman/pkg/*'
# ╔══════════════════════════════════════════════════════════════╗
# ║                     NETWORK / BLUETOOTH                      ║
# ╚══════════════════════════════════════════════════════════════╝
alias httpserver='python -m http.server 8000'
alias blue='bluetoothctl'
alias bluestart='sudo systemctl enable --now bluetooth.service'
alias bluestop='sudo systemctl disable --now bluetooth.service'
# ╔══════════════════════════════════════════════════════════════╗
# ║                      MEDIA / TOOLS                           ║
# ╚══════════════════════════════════════════════════════════════╝
alias music='mpv'
alias record='mkdir -p "$HOME/Videos" && gpu-screen-recorder -w screen -f 60 -q high -cursor no -o "$HOME/Videos/recording-$(date +%Y-%m-%d_%H-%M-%S-%N).mp4"'
alias download='yt-dlp --no-cache-dir --no-playlist -x --audio-format mp3'
alias deskctl='python3 ~/.config/scripts/deskctl.py'
# ╔══════════════════════════════════════════════════════════════╗
# ║                        CLEANUP                               ║
# ╚══════════════════════════════════════════════════════════════╝
alias uninstall='sudo pacman -Rs'
alias uinstall='uninstall'
# ╔══════════════════════════════════════════════════════════════╗
# ║                     EXTERNAL SOURCES                         ║
# ╚══════════════════════════════════════════════════════════════╝
[[ -r ~/.config/ble.sh/out/ble.sh ]] && source ~/.config/ble.sh/out/ble.sh
export LIBCLANG_PATH=/usr/lib
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
