function tick() {
  const now = new Date();
  document.getElementById('clock').textContent =
    String(now.getHours()).padStart(2, '0') + ':' +
    String(now.getMinutes()).padStart(2, '0');
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  document.getElementById('date').textContent =
    days[now.getDay()] + ' ' + now.getDate() + ' ' +
    months[now.getMonth()] + ' ' + now.getFullYear();
}

// Decode the shell-quoted path written by deskctl, without executing the file.
function wallpaperPath(source) {
  const command = source.match(/^feh\s+--no-fehbg\s+--bg-\S+\s+(.+)$/m);
  if (!command) return null;
  const parts = command[1].trim().match(/'[^']*'|"[^"]*"|[^\s'"]+/g);
  if (!parts || parts.join('') !== command[1].trim()) return null;
  const path = parts.map(part =>
    part[0] === "'" || part[0] === '"' ? part.slice(1, -1) : part
  ).join('');
  return path.startsWith('/') ? path : null;
}

let wallpaperLoading = false;
let currentWallpaper = null;

function loadWallpaper() {
  if (wallpaperLoading) return;
  wallpaperLoading = true;
  const request = new XMLHttpRequest();
  request.open('GET', '../../../.fehbg?t=' + Date.now());
  request.timeout = 5000;
  request.onload = () => {
    if (request.status !== 0 && request.status !== 200) return;
    const path = wallpaperPath(request.responseText);
    if (!path || path === currentWallpaper) return;
    const url = 'file://' + path.split('/').map(encodeURIComponent).join('/');
    const image = new Image();
    image.onload = () => {
      document.querySelector('.wallpaper').style.backgroundImage = `url("${url}")`;
      currentWallpaper = path;
    };
    // Keep the existing background if the selected image cannot be loaded.
    image.src = url;
  };
  request.onloadend = () => { wallpaperLoading = false; };
  request.send();
}

let accentLoading = false;

function loadAccent() {
  if (accentLoading) return;
  accentLoading = true;
  // Read deskctl's applied state, not its staged color selection.
  // Use a fresh local-file request so open start pages follow theme changes.
  const request = new XMLHttpRequest();
  request.open('GET', '../../deskctl/session-state.json?t=' + Date.now());
  request.timeout = 5000;
  request.onload = () => {
    if (request.status !== 0 && request.status !== 200) return;
    try {
      const { accent } = JSON.parse(request.responseText);
      if (typeof accent === 'string' && /^#[0-9a-f]{6}$/i.test(accent)) {
        document.documentElement.style.setProperty('--accent', accent);
      }
    } catch {
      // Keep the last color if deskctl is in the middle of writing its state.
    }
  };
  request.onloadend = () => { accentLoading = false; };
  request.send();
}

const bookmarks = document.getElementById('bookmarks');
const bookmarkStatus = document.getElementById('bookmark-status');
let previousBookmarks = null;
let bookmarksLoading = false;

function loadBookmarks() {
  if (bookmarksLoading) return;
  bookmarksLoading = true;
  // XMLHttpRequest supports local files in qutebrowser; fetch does not.
  const request = new XMLHttpRequest();
  request.open('GET', '../bookmarks/urls');
  request.timeout = 5000;
  request.onload = () => {
    if (request.status !== 0 && request.status !== 200) {
      showBookmarkError();
      return;
    }
    const source = request.responseText;
    if (source !== previousBookmarks) {
      const links = document.createDocumentFragment();
      for (const line of source.split(/\r?\n/)) {
        const match = line.trim().match(/^(\S+)(?:\s+(.*))?$/);
        if (!match) continue;
        const [, url, title] = match;
        const link = document.createElement('a');
        link.className = 'link-item';
        link.href = url;
        link.textContent = title || url;
        link.title = title ? `${title}\n${url}` : url;
        links.appendChild(link);
      }
      bookmarks.replaceChildren(links);
      previousBookmarks = source;
    }
    bookmarkStatus.textContent = bookmarks.childElementCount
      ? '' : 'No bookmarks yet. Add one with :bookmark-add.';
    bookmarkStatus.hidden = bookmarks.childElementCount > 0;
  };
  function showBookmarkError() {
    bookmarkStatus.textContent = 'Could not read qutebrowser bookmarks.';
    bookmarkStatus.hidden = false;
  }
  request.onerror = showBookmarkError;
  request.ontimeout = showBookmarkError;
  request.onloadend = () => { bookmarksLoading = false; };
  request.send();
}

let refreshTimer = null;
let clockTimer = null;

function refreshFiles() {
  if (document.hidden) return;
  loadWallpaper();
  loadAccent();
  loadBookmarks();
}

function updateClock() {
  if (document.hidden) return;
  tick();
  clockTimer = setTimeout(updateClock, 60000 - Date.now() % 60000);
}

function syncVisibility() {
  clearInterval(refreshTimer);
  clearTimeout(clockTimer);
  refreshTimer = clockTimer = null;
  if (document.hidden) return;
  updateClock();
  refreshFiles();
  refreshTimer = setInterval(refreshFiles, 2000);
}

window.addEventListener('focus', refreshFiles);
document.addEventListener('visibilitychange', syncVisibility);
syncVisibility();

const searchEngines = {
  'gh':  'https://github.com/search?q=',
  'aw':  'https://wiki.archlinux.org/index.php?search=',
  'yt':  'https://youtube.com/results?search_query=',
  'ddg': 'https://duckduckgo.com/?q=',
};

const sites = {
  'od':   'https://wiki.osdev.org/',
  'lk':   'https://linkedin.com',
  'gm':   'https://mail.google.com',
  'di':   'https://discord.com/app',
  're':   'https://www.reddit.com',
  'cd':   'https://claude.ai',
  'ch':   'https://chatgpt.com',
  'va':   'https://vim-adventures.com',
};

function searchUrl(input) {
  const value = input.trim();
  if (!value) return null;
  if (Object.hasOwn(sites, value)) return sites[value];

  const [, prefix, query = ''] = value.match(/^(\S+)(?:\s+(.*))?$/s);
  if (Object.hasOwn(searchEngines, prefix)) {
    return searchEngines[prefix] + encodeURIComponent(query);
  }
  if (/^https?:\/\//i.test(value) && !/\s/.test(value)) return value;
  if (value.includes('.') && !/\s/.test(value)) return 'https://' + value;
  return searchEngines.ddg + encodeURIComponent(value);
}

document.getElementById('search').addEventListener('keydown', e => {
  if (e.key !== 'Enter') return;
  const url = searchUrl(e.target.value);
  if (url) window.location.href = url;
});
