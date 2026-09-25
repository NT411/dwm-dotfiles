/* See LICENSE file for copyright and license details. */

/* appearance */
static const unsigned int borderpx  = 1;        /* border pixel of windows */
static const unsigned int gappih = 10;
static const unsigned int gappiv = 10;
static const unsigned int gappoh = 16;
static const unsigned int gappov = 16;
static       int smartgaps          = 0;        /* keep outer gaps even when there is only one window */
static const int showbar            = 1;        /* 0 means no bar */
static const int topbar             = 1;        /* 0 means bottom bar */
static const char *fonts[]          = { "JetBrainsMono Nerd Font:size=13" };
static const char dmenufont[]       = "JetBrainsMono Nerd Font:size=13";
static const char col_gray1[]       = "#1e1e2e";
static const char col_gray2[]       = "#45475a";
static const char col_gray3[]       = "#cdd6f4";
static const char col_gray4[]       = "#11111b";
static const char col_cyan[]        = "#ffffff"; 
/* pink: #cba6f7 */
/* blue: #00ffff*/

static const char *colors[][3]      = {
	/*               fg         bg         border   */
	[SchemeNorm] = { col_gray3, col_gray1, col_gray2 },
	[SchemeSel]  = { col_gray4, col_cyan,  col_cyan  },
};

/* tagging */
static const char *tags[] = { "1", "2", "3", "4", "5" };

static const Rule rules[] = {
	/* xprop(1):
	 *	WM_CLASS(STRING) = instance, class
	 *	WM_NAME(STRING) = title
	 */
	/* class      instance    title       tags mask     monitor */
	{ "Gimp",     NULL,       NULL,       0,            -1 },
};

/* layout(s) */

static const float mfact     = 0.55; /* factor of master area size [0.05..0.95] */
static const int nmaster     = 1;    /* number of clients in master area */
static const int resizehints = 0;    /* 1 means respect size hints in tiled resizing */
static const int lockfullscreen = 1; /* 1 will force focus on the fullscreen window */

#define FORCE_VSPLIT 1  /* nrowgrid layout: force two clients to always split vertically */
#include "vanitygaps.c"
#include "tatami.c"

static const Layout layouts[] = {
	/* symbol     arrange function */
    /* first entry is default */
	{ "|+|",      tatami },
	{ "[]=",      tile }, 
	{ "[M]",      monocle },
	{ "[@]",      spiral },
	{ "[\\]",     dwindle },
	{ "H[]",      deck },
	{ "TTT",      bstack },
	{ "===",      bstackhoriz },
	{ "HHH",      grid },
	{ "###",      nrowgrid },
	{ "---",      horizgrid },
	{ ":::",      gaplessgrid },
	{ "|M|",      centeredmaster },
	{ NULL,       NULL },
};

/* key definitions */
#define MODKEY Mod4Mask
#define TAGKEYS(KEY,TAG) \
	{ MODKEY,                       KEY,      view,           {.ui = 1 << TAG} }, \
	{ MODKEY|ControlMask,           KEY,      toggleview,     {.ui = 1 << TAG} }, \
	{ MODKEY|ShiftMask,             KEY,      tag,            {.ui = 1 << TAG} }, \
	{ MODKEY|ControlMask|ShiftMask, KEY,      toggletag,      {.ui = 1 << TAG} },

/* helper for spawning shell commands in the pre dwm-5.0 fashion */
#define SHCMD(cmd) { .v = (const char*[]){ "/bin/sh", "-c", cmd, NULL } }

/* commands */
static char dmenumon[2] = "0"; /* component of dmenucmd, manipulated in spawn() */
static const char *dmenucmd[] = {
	"dmenu-launcher.sh", dmenumon, NULL
};
static const char *termcmd[]  = { "st", NULL };
static const char *nvimcmd[] = { "st", "-e", "nvim", NULL };
static const char *mccmd[] = { "st", "-e", "mc", NULL };
static const char *htopcmd[] = { "st", "-e", "htop", NULL };
static const char *deskctlcmd[] = { "st", "-e", "/bin/sh", "-c", "exec \"$HOME/.config/scripts/deskctl.py\"", NULL };
static const char *slockcmd[] = { "slock", NULL };
static const char *screenshotcmd[] = {"/bin/sh", "-c","mkdir -p \"$HOME/Images\" && ""gpu-screen-recorder -w screen " "-cursor no " "-o \"$HOME/Images/screenshot-$(date +%Y-%m-%d_%H-%M-%S-%N).jpg\"",NULL};
static const Key keys[] = {
	/* Audio keys follow the default PipeWire output/input. */
	{ 0, XF86XK_AudioRaiseVolume, spawn, SHCMD("wpctl set-volume -l 1.0 @DEFAULT_AUDIO_SINK@ 5%+ && pkill -USR1 -u \"$(id -u)\" -x slstatus") },
	{ 0, XF86XK_AudioLowerVolume, spawn, SHCMD("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%- && pkill -USR1 -u \"$(id -u)\" -x slstatus") },
	{ 0, XF86XK_AudioMute, spawn, SHCMD("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle && pkill -USR1 -u \"$(id -u)\" -x slstatus") },
	{ 0, XF86XK_AudioMicMute, spawn, SHCMD("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle") },

	/* apps */
	{ MODKEY,                       XK_m,            spawn,          {.v = mccmd    } },
	{ MODKEY,                       XK_h,            spawn,          {.v = htopcmd  } },
	{ MODKEY,                       XK_p,            spawn,          {.v = dmenucmd } },
	{ MODKEY,                       XK_d,            spawn,          {.v = deskctlcmd } },
	{ MODKEY,                       XK_Return,       spawn,          {.v = termcmd  } },
	{ MODKEY,                       XK_v,            spawn,          {.v = nvimcmd } },
	{ MODKEY,                       XK_s,            spawn,          {.v = screenshotcmd } },
	{ MODKEY,                       XK_b,            spawn,          SHCMD("qutebrowser") },

	/* focus */
    { MODKEY,                       XK_Left,  focusstackorview, {.i = -1 } },
    { MODKEY,                       XK_Right, focusstackorview, {.i = +1 } },
   /*move */
    { MODKEY|Mod1Mask,              XK_Left,  movestackortag,  {.i = -1 } },
    { MODKEY|Mod1Mask,              XK_Right, movestackortag,  {.i = +1 } },

	/* layouts */
    { MODKEY,                       XK_bracketright, cyclelayout, {.i = +1} },
    { MODKEY,                       XK_bracketleft,  cyclelayout, {.i = -1} },
    { MODKEY|ShiftMask,             XK_t,            setlayout, {.v = &layouts[0]} },   // tatami
    { MODKEY|ShiftMask,             XK_y,            setlayout, {.v = &layouts[1]} },   // tile
    { MODKEY|ShiftMask,             XK_m,            setlayout, {.v = &layouts[2]} },   // monocle


	/* actions */
	{ MODKEY,                       XK_l,            spawn,          {.v = slockcmd } },
	{ MODKEY,                       XK_x,            killclient,     {0} },
	{ MODKEY|ShiftMask,             XK_Return,       zoom,           {0} },

	/* gaps */
	{ MODKEY|Mod1Mask,              XK_u,            incrgaps,       {.i = +1 } },
	{ MODKEY|Mod1Mask|ShiftMask,    XK_u,            incrgaps,       {.i = -1 } },
	{ MODKEY|Mod1Mask,              XK_0,            togglegaps,     {0} },

	/* bar */
	{ MODKEY|ShiftMask,             XK_b,            togglebar,      {0} },

	/* monitor */
	{ MODKEY,                       XK_comma,        focusmon,       {.i = -1 } },
	{ MODKEY,                       XK_period,       focusmon,       {.i = +1 } },

	/* tags */
	TAGKEYS( XK_1, 0)
	TAGKEYS( XK_2, 1)
	TAGKEYS( XK_3, 2)
	TAGKEYS( XK_4, 3)
	TAGKEYS( XK_5, 4)

	/* quit */
	{ MODKEY|Mod1Mask, XK_q, quit, {0} },
};

/* button definitions */
/* click can be ClkTagBar, ClkLtSymbol, ClkStatusText, ClkWinTitle, ClkClientWin, or ClkRootWin */
static const Button buttons[] = {
	/* click                event mask      button          function        argument */
	{ ClkLtSymbol,          0,              Button1,        cyclelayout,    {.i = +1} },
	{ ClkLtSymbol,          0,              Button3,        cyclelayout,    {.i = -1} },
	{ ClkLtSymbol,          0,              Button4,        cyclelayout,    {.i = -1} },
	{ ClkLtSymbol,          0,              Button5,        cyclelayout,    {.i = +1} },
	{ ClkWinTitle,          0,              Button2,        zoom,           {0} },
	{ ClkStatusText,        0,              Button2,        spawn,          {.v = termcmd } },
	{ ClkTagBar,            0,              Button1,        view,           {0} },
	{ ClkTagBar,            0,              Button3,        toggleview,     {0} },
	{ ClkTagBar,            MODKEY,         Button1,        tag,            {0} },
	{ ClkTagBar,            MODKEY,         Button3,        toggletag,      {0} },
};
