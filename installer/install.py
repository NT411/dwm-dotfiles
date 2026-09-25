#!/usr/bin/env python3
"""Install the bundled local configuration; no dotfile downloads or AUR repos."""
import argparse
import datetime
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import time

REPO = Path(__file__).resolve().parents[1]
COMPONENTS = ('dwm', 'dmenu', 'st', 'slstatus', 'slock', 'st/scroll')


def run(argv, **kwargs):
    print('+ ' + ' '.join(map(str, argv)), flush=True)
    subprocess.run(list(map(str, argv)), check=True, **kwargs)


def exists(path):
    return path.exists() or path.is_symlink()


def save_json(path, data):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(path)


def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.is_symlink():
        target.symlink_to(os.readlink(source))
    elif source.is_dir():
        shutil.copytree(source, target, symlinks=True)
    else:
        shutil.copy2(source, target)


def safe_target(home, rel):
    rel = Path(rel)
    if rel.is_absolute() or '..' in rel.parts or not rel.parts:
        raise RuntimeError(f'Invalid destination: {rel}')
    dest = home / rel
    # Never follow an existing parent symlink out of the selected home.
    if not dest.parent.resolve().is_relative_to(home):
        raise RuntimeError(f'Destination escapes selected home: {dest}')
    return dest


class Deployment:
    def __init__(self, home):
        self.home = home
        root = home / '.RiceBackup'
        if not root.resolve().is_relative_to(home):
            raise RuntimeError('Backup directory escapes selected home')
        root.mkdir(parents=True, exist_ok=True)
        self.backup = Path(tempfile.mkdtemp(prefix='dwm-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S-'), dir=root))
        self.entries = []
        self.created_ns = time.time_ns()
        self.save()

    def save(self):
        path = self.backup / 'manifest.json'
        save_json(path, {'home': str(self.home), 'created_ns': self.created_ns,
                         'entries': self.entries})

    def put(self, source, rel):
        dest = safe_target(self.home, rel)
        saved = self.backup / 'original' / rel
        had_original = exists(dest)
        if had_original:
            # Copy first, so a failed backup cannot remove the active file.
            copy(dest, saved)
        entry = {'path': str(rel), 'original': had_original}
        self.entries.append(entry)
        self.save()
        if exists(dest):
            if dest.is_dir() and not dest.is_symlink():
                shutil.rmtree(dest)
            else:
                dest.unlink()
        copy(source, dest)


def restore(backup, home):
    data = json.loads((backup / 'manifest.json').read_text())
    if Path(data['home']) != home:
        raise RuntimeError('Backup belongs to a different target home')
    if (backup / 'restored').exists():
        raise RuntimeError('This backup has already been restored')
    progress_path = backup / 'restore-progress.json'
    progress = json.loads(progress_path.read_text()) if progress_path.exists() else {}
    for index, entry in reversed(list(enumerate(data['entries']))):
        key = str(index)
        step = progress.get(key, {})
        if step.get('done'):
            continue
        dest = safe_target(home, entry['path'])
        saved = backup / 'original' / entry['path']
        displaced = backup / 'replaced-on-restore' / entry['path']
        print(f'Restore {dest}')
        if not step:
            if exists(displaced):
                raise RuntimeError(f'Older interrupted restore needs manual review: {displaced}')
            dest.parent.mkdir(parents=True, exist_ok=True)
            # Stage on the destination filesystem, so the final rename is atomic.
            staging = Path(tempfile.mkdtemp(prefix='.rice-restore-', dir=dest.parent))
            step = {'staging': str(staging), 'ready': False, 'had_dest': exists(dest)}
            progress[key] = step
            save_json(progress_path, progress)
        staging = Path(step['staging'])
        if staging.parent != dest.parent or not staging.name.startswith('.rice-restore-'):
            raise RuntimeError('Invalid restore staging path')
        staged = staging / 'original'
        if not step['ready']:
            if exists(staged):
                if staged.is_dir() and not staged.is_symlink():
                    shutil.rmtree(staged)
                else:
                    staged.unlink()
            if entry['original']:
                copy(saved, staged)
            step['ready'] = True
            save_json(progress_path, progress)
        # A displacement already present means that rename finished before an
        # interruption. Never overwrite it or move a restored original into it.
        if step['had_dest'] and not exists(displaced):
            displaced.parent.mkdir(parents=True, exist_ok=True)
            dest.rename(displaced)
        if entry['original'] and exists(staged):
            if exists(dest):
                raise RuntimeError(f'Destination changed during restore: {dest}')
            staged.rename(dest)
        elif entry['original'] and not exists(dest):
            raise RuntimeError(f'Restored destination is missing: {dest}')
        elif not entry['original'] and exists(dest):
            raise RuntimeError(f'Destination changed during restore: {dest}')
        step['done'] = True
        save_json(progress_path, progress)
        staging.rmdir()
    (backup / 'restored').touch()


def packages():
    return [s for line in (REPO / 'installer/packages.txt').read_text().splitlines()
            if (s := line.strip()) and not s.startswith('#')]


def install_packages(logdir):
    if not shutil.which('pacman'):
        raise RuntimeError('Package installation requires Arch Linux')
    # A full upgrade avoids a partial Arch upgrade. Keep pacman's own confirmation.
    command = ['sudo', 'pacman', '-Syu', '--needed', *packages()]
    try:
        run(command)
    except subprocess.CalledProcessError:
        print('Package transaction failed. Retrying once; pacman will ask again.')
        try:
            run(command)
        except subprocess.CalledProcessError:
            (logdir / 'missing-packages.txt').write_text('Package transaction failed twice. Check pacman output.\n' + '\n'.join(packages()) + '\n')
            raise
    missing = [p for p in packages() if subprocess.run(['pacman', '-Q', p], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode]
    if missing:
        (logdir / 'missing-packages.txt').write_text('\n'.join(missing) + '\n')
        raise RuntimeError('Missing dependencies; see missing-packages.txt in the log directory')


def build(stage, logdir):
    for component in COMPONENTS:
        directory = stage / 'config' / component
        logfile = logdir / (component.replace('/', '-') + '.log')
        print(f'Build {component} (log: {logfile})', flush=True)
        with logfile.open('w') as log:
            subprocess.run(['make', '-C', str(directory), 'clean'], stdout=log, stderr=subprocess.STDOUT, check=True)
            subprocess.run(['make', '-C', str(directory)], stdout=log, stderr=subprocess.STDOUT, check=True)
    terminfo = stage / 'terminfo'
    terminfo.mkdir()
    run(['tic', '-sx', '-o', terminfo, stage / 'config/st/st.info'])


def payload(stage):
    result = []
    # Replace source trees together so old objects cannot affect later deskctl builds.
    for name in ('dwm', 'dmenu', 'st', 'slstatus', 'slock', 'ble.sh'):
        result.append((stage / 'config' / name, Path('.config') / name))
    # Deploy Neovim as a complete tree so old plugin files cannot alter the setup.
    result.append((stage / 'config/nvim', Path('.config/nvim')))
    for name in ('picom', 'gtk-3.0', 'gtk-4.0', 'scripts', 'micro', 'qutebrowser',
                 'htop', 'mc', 'lazygit', 'deskctl', 'systemd', 'gh', 'GIMP', 'qBittorrent'):
        for source in sorted((stage / 'config' / name).rglob('*')):
            if source.is_file() or source.is_symlink():
                result.append((source, Path('.config') / source.relative_to(stage / 'config')))
    for source in sorted((stage / 'home').iterdir()):
        result.append((source, Path(source.name)))
    for source in sorted((stage / 'misc/wallpapers').iterdir()):
        result.append((source, Path('Images/Wallpapers') / source.name))
    for source in sorted((stage / 'misc/mc/skins').iterdir()):
        if source.is_file() or source.is_symlink():
            result.append((source, Path('.local/share/mc/skins') / source.name))
    # Relative links keep deskctl's in-place rebuilds effective.
    bindir = stage / 'bin'
    bindir.mkdir()
    for name, target in {'dwm': 'dwm/dwm', 'st': 'st/st', 'slstatus': 'slstatus/slstatus',
                         'dmenu': 'dmenu/dmenu', 'dmenu_run': 'dmenu/dmenu_run',
                         'dmenu_path': 'dmenu/dmenu_path', 'stest': 'dmenu/stest',
                         'dmenu-launcher.sh': 'dmenu/dmenu-launcher.sh',
                         'scroll': 'st/scroll/scroll', 'deskctl': 'scripts/deskctl.py'}.items():
        source = bindir / name
        source.symlink_to('../../.config/' + target)
        result.append((source, Path('.local/bin') / name))
    source = bindir / 'slock'
    source.symlink_to('/usr/local/bin/slock')
    result.append((source, Path('.local/bin/slock')))
    if (stage / 'terminfo').exists():
        for source in sorted((stage / 'terminfo').rglob('*')):
            if source.is_file() or source.is_symlink():
                result.append((source, Path('.terminfo') / source.relative_to(stage / 'terminfo')))
    return result


def install_system(stage, backup):
    # Keep privileged files outside user-writable source trees.
    sysbackup = Path('/var/backups/dwm-dotfiles') / backup.name
    run(['sudo', 'mkdir', '-p', sysbackup])
    launcher = stage / 'dwm-local-session'
    launcher.write_text('#!/bin/sh\nexec "$HOME/.config/dwm/start-dwm.sh"\n')
    desktop = stage / 'dwm-local.desktop'
    desktop.write_text('[Desktop Entry]\nName=DWM (local dotfiles)\nComment=Local DWM session\nExec=/usr/local/bin/dwm-local-session\nType=Application\nDesktopNames=dwm\n')
    targets = [(stage / 'config/slock/slock', '/usr/local/bin/slock', '4755'),
               (launcher, '/usr/local/bin/dwm-local-session', '755'),
               (desktop, '/usr/share/xsessions/dwm-local.desktop', '644')]
    for source in sorted((stage / 'system/etc/X11/xorg.conf.d').glob('*.conf')):
        targets.append((source, '/etc/X11/xorg.conf.d/' + source.name, '644'))
    journal = {'backup': str(sysbackup), 'targets': []}
    journal_path = backup / 'system-files.json'
    for source, target, mode in targets:
        if exists(Path(target)):
            run(['sudo', 'cp', '-a', '--parents', target, sysbackup])
        journal['targets'].append({'path': target, 'original': exists(Path(target))})
        journal_path.write_text(json.dumps(journal, indent=2) + '\n')
        run(['sudo', 'install', '-D', '-o', 'root', '-g', 'root', '-m', mode, source, target])
    print(f'System-file backups: {sysbackup}')


def latest_backup(home):
    backups = [path for path in (home / '.RiceBackup').glob('dwm-*')
               if (path / 'manifest.json').is_file() and not (path / 'restored').exists()]
    if not backups:
        raise RuntimeError('No unrestored home backup found in ~/.RiceBackup')
    def creation_key(path):
        data = json.loads((path / 'manifest.json').read_text())
        if isinstance(data.get('created_ns'), int):
            return data['created_ns'], path.name
        # Old backups encode creation time in their name; directory mtime changes
        # during recovery and must not affect ordering.
        created = datetime.datetime.strptime(path.name[4:19], '%Y%m%d-%H%M%S')
        return int(created.timestamp() * 1_000_000_000), path.name
    return max(backups, key=creation_key)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', nargs='?', choices=('install', 'restore'))
    args = parser.parse_args()
    if args.action is None:
        tittle = ("""
▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
▐                      █████                                                    ▌
▐                     ░░███                                                     ▌
▐                   ███████  █████ ███ █████ █████████████                      ▌
▐                  ███░░███ ░░███ ░███░░███ ░░███░░███░░███                     ▌
▐                 ░███ ░███  ░███ ░███ ░███  ░███ ░███ ░███                     ▌
▐                 ░███ ░███  ░░███████████   ░███ ░███ ░███                     ▌
▐                 ░░████████  ░░████░████    █████░███ █████                    ▌
▐                  ░░░░░░░░    ░░░░ ░░░░    ░░░░░ ░░░ ░░░░░                     ▌
▐                                                                               ▌
▐          █████           █████       ██████   ███  ████                       ▌
▐         ░░███           ░░███       ███░░███ ░░░  ░░███                       ▌
▐       ███████   ██████  ███████    ░███ ░░░  ████  ░███   ██████   █████      ▌
▐      ███░░███  ███░░███░░░███░    ███████   ░░███  ░███  ███░░███ ███░░       ▌
▐     ░███ ░███ ░███ ░███  ░███    ░░░███░     ░███  ░███ ░███████ ░░█████      ▌
▐     ░███ ░███ ░███ ░███  ░███ ███  ░███      ░███  ░███ ░███░░░   ░░░░███     ▌
▐     ░░████████░░██████   ░░█████   █████     █████ █████░░██████  ██████      ▌
▐      ░░░░░░░░  ░░░░░░     ░░░░░   ░░░░░     ░░░░░ ░░░░░  ░░░░░░  ░░░░░░       ▌
▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
""")
        print(tittle)
        print('1) install\n2) restore\n3) exit')
        choice = input('Choose: ').strip().lower()
        if choice in ('3', 'exit'):
            sys.exit(0)
        args.action = {'1': 'install', '2': 'restore'}.get(choice, choice)
        if args.action not in ('install', 'restore'):
            parser.error('choose install, restore, or exit')
    home = Path.home().resolve()
    if os.geteuid() == 0:
        parser.error('run as your normal user; privileged actions use sudo')
    if home == Path('/') or home == REPO or home.is_relative_to(REPO):
        parser.error('target home must be outside the repository and cannot be /')
    if args.action == 'restore':
        backup = latest_backup(home)
        print(f'Home backup: {backup}')
        restore(backup, home)
        print('Home restore complete. System files and packages require separate review; see README.')
        return
    print(f'DWM local dotfiles → {home}\nComponents: {", ".join(COMPONENTS)}')
    logdir = Path(tempfile.mkdtemp(prefix='dwm-install-logs-'))
    print(f'Logs: {logdir}', flush=True)
    install_packages(logdir)
    with tempfile.TemporaryDirectory(prefix='dwm-build-') as temporary:
        stage = Path(temporary)
        for name in ('config', 'home', 'misc', 'system'):
            shutil.copytree(REPO / name, stage / name, symlinks=True)
        wallpaper = home / 'Images/Wallpapers/wp2.png'
        (stage / 'home/.fehbg').write_text(
            f'#!/bin/sh\nfeh --no-fehbg --bg-scale {shlex.quote(str(wallpaper))}\n')
        build(stage, logdir)
        items = payload(stage)
        for _, rel in items:
            safe_target(home, rel)
        deployment = Deployment(home)
        print(f'Home backup: {deployment.backup}', flush=True)
        try:
            for source, rel in items:
                deployment.put(source, rel)
        except BaseException:
            print('Home deployment failed; restoring replaced files.', file=sys.stderr)
            restore(deployment.backup, home)
            raise
        install_system(stage, deployment.backup)
        print('Installed. Log out and select DWM (local dotfiles), or run startx from a TTY.')
        print(f'Restore home files: {REPO / "RiceInstaller"} restore')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f'Installation failed: {error}', file=sys.stderr)
        sys.exit(1)
