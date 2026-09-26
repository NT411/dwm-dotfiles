/* user and group to drop privileges to */
static const char *user  = "nobody";
static const char *group = "nogroup";

static const char *colorname[NUMCOLS] = {
	[INIT] =   "black",     /* after initialization */
	[INPUT] =  "#005577",   /* during input */
	[FAILED] = "#cc3333",   /* wrong password */
};

/* lock screen opacity */
static const float alpha = 1;

/* treat a cleared input like a wrong password (color) */
static const int failonclear = 1;
