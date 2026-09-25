local map = vim.keymap.set

local function cmd(command)
  return "<cmd>" .. command .. "<cr>"
end

local function pick(command, opts)
  return function()
    LazyVim.pick.open(command, opts)
  end
end

local function save()
  if vim.bo.buftype == "" then
    vim.cmd.write()
  end
end

local function select_all()
  vim.cmd.normal({ args = { "ggVG" }, bang = true })
end

local function leave_insert_like_mode()
  local mode = vim.fn.mode()
  if mode ~= "n" and mode ~= "no" then
    vim.cmd.stopinsert()
  end
end

local opts = { silent = true }

map({ "n", "i", "v" }, "<C-s>", function()
  if vim.fn.mode() ~= "n" then
    vim.cmd.stopinsert()
  end
  save()
end, vim.tbl_extend("force", opts, { desc = "Save File" }))

map("n", "<C-p>", pick("files"), { desc = "Find Files" })
map("n", "<C-S-p>", pick("commands"), { desc = "Command Palette" })
map("n", "<leader>p", pick("commands"), { desc = "Command Palette" })
map("n", "<C-f>", pick("blines"), { desc = "Find in File" })
map("n", "<C-h>", pick("live_grep"), { desc = "Find in Project" })
local function toggle_explorer()
  leave_insert_like_mode()
  vim.cmd("Neotree toggle")
end

map({ "n", "i", "t" }, "<C-b>", toggle_explorer, { desc = "Toggle Explorer" })
local function toggle_terminal()
  leave_insert_like_mode()
  Snacks.terminal()
end

map({ "n", "i", "t" }, "<C-`>", toggle_terminal, { desc = "Toggle Terminal" })
map({ "n", "i", "t" }, "<C-Space>", toggle_terminal, { desc = "Toggle Terminal" })
map({ "n", "i", "t" }, "<C-@>", toggle_terminal, { desc = "Toggle Terminal" })
map({ "n", "i", "t" }, "<Nul>", toggle_terminal, { desc = "Toggle Terminal" })
map({ "n", "i", "t" }, "<leader>t", toggle_terminal, { desc = "Toggle Terminal" })

map("n", "<C-n>", cmd("enew"), { desc = "New File" })
map("n", "<C-o>", pick("oldfiles"), { desc = "Open Recent" })
map("n", "<C-w>", cmd("bd"), { desc = "Close Editor" })
map("n", "<C-Tab>", cmd("bnext"), { desc = "Next Editor" })
map("n", "<C-S-Tab>", cmd("bprevious"), { desc = "Previous Editor" })

map("n", "<C-z>", "u", { desc = "Undo" })
map("i", "<C-z>", "<C-o>u", { desc = "Undo" })
map("n", "<C-y>", "<C-r>", { desc = "Redo" })
map("i", "<C-y>", "<C-o><C-r>", { desc = "Redo" })
map({ "n", "v" }, "<C-a>", select_all, { desc = "Select All" })

map("v", "<C-c>", '"+y', { desc = "Copy" })
map("n", "<C-c>", '"+yy', { desc = "Copy Line" })
map("v", "<C-x>", '"+d', { desc = "Cut" })
map("n", "<C-x>", '"+dd', { desc = "Cut Line" })
map("n", "<C-v>", '"+p', { desc = "Paste" })
map("x", "<C-v>", '"+P', { desc = "Paste" })
map("i", "<C-v>", '<C-r>+', { desc = "Paste" })

map("n", "<C-/>", "gcc", { remap = true, desc = "Toggle Comment" })
map("x", "<C-/>", "gc", { remap = true, desc = "Toggle Comment" })
map("n", "<C-_>", "gcc", { remap = true, desc = "Toggle Comment" })
map("x", "<C-_>", "gc", { remap = true, desc = "Toggle Comment" })
map("n", "<A-z>", cmd("set wrap!"), { desc = "Toggle Word Wrap" })

map("n", "<F2>", vim.lsp.buf.rename, { desc = "Rename Symbol" })
map("n", "<F12>", vim.lsp.buf.definition, { desc = "Go to Definition" })
map("n", "<S-F12>", vim.lsp.buf.references, { desc = "Find References" })
map("n", "<A-CR>", vim.lsp.buf.code_action, { desc = "Quick Fix / Code Action" })
map({ "n", "v" }, "<S-A-f>", function()
  require("conform").format({ async = true, lsp_format = "fallback" })
end, { desc = "Format Document" })
map("n", "<C-S-m>", cmd("Trouble diagnostics toggle"), { desc = "Problems" })
map("n", "<C-S-o>", cmd("Outline"), { desc = "Outline" })

map("n", "<Esc>", cmd("nohlsearch"), { desc = "Clear Search Highlight" })
