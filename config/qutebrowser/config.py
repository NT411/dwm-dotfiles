config.load_autoconfig(False)
c.url.start_pages = ["~/.config/qutebrowser/startpage/index.html"]
c.url.default_page = c.url.start_pages[0]

# Ad and tracker blocking. Refresh lists with :adblock-update.
c.content.blocking.enabled = True
c.content.blocking.method = "both"
c.content.blocking.adblock.lists = [
    "https://easylist.to/easylist/easylist.txt",
    "https://easylist.to/easylist/easyprivacy.txt",
    "https://ublockorigin.github.io/uAssets/filters/badware.txt",
]
c.content.blocking.hosts.lists = [
    "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",
]

# Privacy defaults with permission prompts for features you may need.
c.content.cookies.accept = "no-3rdparty"
c.content.notifications.enabled = False
c.content.autoplay = False
c.content.webrtc_ip_handling_policy = "disable-non-proxied-udp"
c.content.geolocation = "ask"
c.content.media.audio_capture = "ask"
c.content.media.video_capture = "ask"
c.content.media.audio_video_capture = "ask"
c.content.javascript.clipboard = "ask"
c.content.dns_prefetch = False
c.content.hyperlink_auditing = False

# Keep graphics and the local bookmark-powered start page working.
c.content.canvas_reading = True
c.content.webgl = True

# Dark websites and browser interface, with rose accents matching the start page.
c.colors.webpage.preferred_color_scheme = "dark"
c.colors.webpage.darkmode.enabled = True
c.colors.webpage.darkmode.policy.images = "smart"
c.colors.webpage.bg = "#0e0e12"
c.colors.tabs.bar.bg = "#0e0e12"
c.colors.tabs.even.bg = "#181820"
c.colors.tabs.odd.bg = "#181820"
c.colors.tabs.even.fg = "#cdd6f4"
c.colors.tabs.odd.fg = "#cdd6f4"
c.colors.tabs.selected.even.bg = "#34303e"
c.colors.tabs.selected.odd.bg = "#34303e"
c.colors.tabs.selected.even.fg = "#ffffff"
c.colors.tabs.selected.odd.fg = "#ffffff"
c.colors.statusbar.normal.bg = "#0e0e12"
c.colors.statusbar.normal.fg = "#cdd6f4"
c.colors.statusbar.command.bg = "#181820"
c.colors.statusbar.command.fg = "#cdd6f4"
c.colors.completion.even.bg = "#0e0e12"
c.colors.completion.odd.bg = "#181820"
c.colors.completion.fg = "#cdd6f4"
c.colors.completion.category.bg = "#181820"
c.colors.completion.category.fg = "#c4707a"
c.colors.completion.category.border.top = "#181820"
c.colors.completion.category.border.bottom = "#181820"
c.colors.completion.item.selected.bg = "#34303e"
c.colors.completion.item.selected.fg = "#ffffff"
c.colors.completion.item.selected.border.top = "#c4707a"
c.colors.completion.item.selected.border.bottom = "#c4707a"
c.colors.completion.match.fg = "#c4707a"
c.colors.prompts.bg = "#181820"
c.colors.prompts.fg = "#cdd6f4"
c.colors.prompts.selected.bg = "#34303e"
