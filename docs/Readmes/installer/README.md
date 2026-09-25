# Installer

[RiceInstaller](../../../RiceInstaller) is the shell entry point for [install.py](../../../installer/install.py). Run it as your normal user on Arch Linux; privileged operations use `sudo`.

## Commands

From the repository root:

```sh
./RiceInstaller          # Interactive install/restore menu
./RiceInstaller install # Install directly
./RiceInstaller restore # Restore the latest unrestored home backup
./RiceInstaller --help  # Show command-line help
```

Python 3 is needed to start the installer. Installation also needs `sudo`, `pacman`, and network access for package installation.

## Installation behavior

1. Runs `sudo pacman -Syu --needed` with [packages.txt](../../../installer/packages.txt), keeping Pacman's confirmation prompt.
2. Copies the bundled configuration to a temporary staging directory and builds DWM, Dmenu, ST, Slstatus, Slock, and ST's scroll helper. It also compiles ST terminfo.
3. Backs up replaced home files and deploys configuration, scripts, wallpaper, shell files, and command links. Several configuration directories, including Neovim, are replaced as complete trees.
4. Installs the root-owned Slock executable, an X session launcher and display-manager entry, and the bundled Xorg configuration.

During staging, the installer writes the user's absolute path to the default wallpaper into `.fehbg`. This lets the browser start page read the wallpaper immediately after installation. Selecting another wallpaper in deskctl updates that path later.

Build logs are stored in the printed `/tmp/dwm-install-logs-*` directory. Pacman output is shown in the terminal and is not captured there; package failures produce a `missing-packages.txt` summary or list. Source code comes from this repository; the installer does not fetch external dotfile trees or AUR repositories.

After installation, run `startx` from a TTY or select **DWM (local dotfiles)** in a display manager. Neovim downloads its plugins on first launch.

## Backups and recovery

Home backups are stored in `~/.RiceBackup/dwm-*`, with a `manifest.json` recording the deployed paths. Restore selects the newest backup that has not already been restored. Files displaced during recovery are retained in that backup's `replaced-on-restore/` directory. Recovery needs an existing backup.

A failure during home-file deployment triggers home restoration automatically. System-file installation happens afterward and is not covered by that rollback.

**Restore only recovers home files.** It does not undo package installation or system-file changes. System originals are saved under `/var/backups/dwm-dotfiles/<backup-name>`; the home backup's `system-files.json` records the affected paths for separate manual recovery.

[Back to documentation](../../../README.md#documentation)

[Documentation index](../../../README.md#documentation)
