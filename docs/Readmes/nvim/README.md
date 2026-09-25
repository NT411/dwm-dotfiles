# Neovim

A LazyVim-based configuration with a VS Code-style theme and custom keyboard shortcuts. The [installer](../installer/README.md) deploys this directory to `~/.config/nvim`.

## First launch

Open Neovim with **Super + V** in DWM or run `nvim`. The configuration bootstraps `lazy.nvim` through Git and installs plugins, so the first launch needs network access. Use `:Lazy` to inspect plugin installation and `:checkhealth` to diagnose setup problems.

Automatic plugin update checks are disabled. Run `:Lazy check` when you want to check for updates.

The installer package list includes Neovim, Git, ripgrep, fd, fzf, Node.js, npm, unzip, xclip, and build tools used by this editor setup. JetBrainsMono Nerd Font supplies UI icons.

## Configuration files

| File | Purpose |
| --- | --- |
| [init.lua](../../../config/nvim/init.lua) | Configuration entry point |
| [lua/config/lazy.lua](../../../config/nvim/lua/config/lazy.lua) | Plugin manager bootstrap and LazyVim extras |
| [lua/config/options.lua](../../../config/nvim/lua/config/options.lua) | Editor options, leaders, and picker selection |
| [lua/config/keymaps.lua](../../../config/nvim/lua/config/keymaps.lua) | Custom shortcuts |
| [lua/config/autocmds.lua](../../../config/nvim/lua/config/autocmds.lua) | Event-driven editor behavior |
| [lua/plugins/](../../../config/nvim/lua/plugins) | Theme, UI, and language-server customizations |
| [lazy-lock.json](../../../config/nvim/lazy-lock.json) | Locked plugin revisions |

The leader key is **Space**. Indentation uses two spaces, the system clipboard is enabled, and automatic formatting is disabled. The configuration uses fzf-lua for search, Neo-tree for the explorer, and Snacks for the terminal.

See [Neovim keybindings](KEYBINDINGS.md) for the full custom shortcut reference. Common shortcuts include **Ctrl + S** to save, **Ctrl + P** to find files, **Ctrl + B** to toggle the explorer, and **Space then T** to toggle the terminal.

[Back to documentation](../../../README.md#documentation)

[Documentation index](../../../README.md#documentation)
