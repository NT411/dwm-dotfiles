# Neovim Keybindings

This config uses LazyVim with a VS Code-style custom keymap layer.

- Leader: `Space`
- Local leader: `\`
- Picker: `fzf-lua`
- Explorer: `neo-tree`
- Terminal: `snacks.nvim`

LazyVim's default mappings still apply. This document focuses on the custom mappings defined in `lua/config/keymaps.lua`.

## File And Command Navigation

| Key | Mode | Action |
| --- | --- | --- |
| `Ctrl+s` | Normal, Insert, Visual | Save current file |
| `Ctrl+p` | Normal | Find files |
| `Ctrl+Shift+p` | Normal | Command palette |
| `Space p` | Normal | Command palette |
| `Ctrl+f` | Normal | Find in current file |
| `Ctrl+h` | Normal | Find in project |
| `Ctrl+o` | Normal | Open recent files |
| `Ctrl+n` | Normal | New empty buffer |
| `Ctrl+w` | Normal | Close current buffer |
| `Ctrl+Tab` | Normal | Next buffer |
| `Ctrl+Shift+Tab` | Normal | Previous buffer |

## Explorer And Terminal

| Key | Mode | Action |
| --- | --- | --- |
| `Ctrl+b` | Normal, Insert, Terminal | Toggle file explorer |
| `Ctrl+Backtick` | Normal, Insert, Terminal | Toggle terminal |
| `Ctrl+Space` | Normal, Insert, Terminal | Toggle terminal |
| `Ctrl+@` | Normal, Insert, Terminal | Toggle terminal |
| `Nul` | Normal, Insert, Terminal | Toggle terminal |
| `Space t` | Normal, Insert, Terminal | Toggle terminal |

## Editing

| Key | Mode | Action |
| --- | --- | --- |
| `Ctrl+z` | Normal, Insert | Undo |
| `Ctrl+y` | Normal, Insert | Redo |
| `Ctrl+a` | Normal, Visual | Select all |
| `Ctrl+c` | Visual | Copy selection to system clipboard |
| `Ctrl+c` | Normal | Copy current line to system clipboard |
| `Ctrl+x` | Visual | Cut selection to system clipboard |
| `Ctrl+x` | Normal | Cut current line to system clipboard |
| `Ctrl+v` | Normal, Visual | Paste from system clipboard |
| `Ctrl+v` | Insert | Paste from system clipboard |
| `Ctrl+/` | Normal, Visual | Toggle comment |
| `Ctrl+_` | Normal, Visual | Toggle comment |
| `Alt+z` | Normal | Toggle word wrap |
| `Esc` | Normal | Clear search highlight |

## LSP And Code Tools

| Key | Mode | Action |
| --- | --- | --- |
| `F2` | Normal | Rename symbol |
| `F12` | Normal | Go to definition |
| `Shift+F12` | Normal | Find references |
| `Alt+Enter` | Normal | Quick fix / code action |
| `Shift+Alt+f` | Normal, Visual | Format document or selection |
| `Ctrl+Shift+m` | Normal | Toggle diagnostics/problems |
| `Ctrl+Shift+o` | Normal | Toggle outline |

## Built-In Behavior From Options

These are not keybindings, but they affect editing behavior:

| Setting | Behavior |
| --- | --- |
| `clipboard=unnamedplus` | Yank, delete, and paste use the system clipboard by default |
| `autowrite=true` | Neovim can automatically write changed buffers before some commands |
| `mouse=a` | Mouse support is enabled |
| `tabstop=2`, `shiftwidth=2`, `expandtab=true` | Indentation uses two spaces |
| `wrap=false` | Lines do not wrap by default; use `Alt+z` to toggle |

## Autocommands

| Event | Behavior |
| --- | --- |
| Text yank | Highlight yanked text |
| Buffer read | Return to the last edit position when reopening a file |

## Plugin Notes

| Plugin | Purpose |
| --- | --- |
| `LazyVim` | Base distribution and default mappings |
| `fzf-lua` | File, command, line, and project search |
| `neo-tree.nvim` | File explorer |
| `snacks.nvim` | Terminal and UI helpers |
| `conform.nvim` | Formatting |
| `trouble.nvim` | Diagnostics/problems view |
| `outline.nvim` | Symbol outline |
| `vscode.nvim` | VS Code-style colorscheme |

[Documentation index](../../../README.md#documentation)
