/* See LICENSE file for copyright and license details. */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "../util.h"

const char *
updates(const char *interval)
{
	static char count[16] = "0";
	static time_t last;
	FILE *fp;
	long ttl;
	time_t now;

	ttl = interval ? strtol(interval, NULL, 10) : 1800;
	now = time(NULL);

	if (last && ttl > 0 && now - last < ttl)
		return count;

	if (!(fp = popen("checkupdates 2>/dev/null | wc -l", "r"))) {
		warn("popen 'checkupdates':");
		return NULL;
	}

	if (fscanf(fp, "%15s", count) != 1) {
		pclose(fp);
		return NULL;
	}

	if (pclose(fp) < 0) {
		warn("pclose 'checkupdates':");
		return NULL;
	}

	last = now;
	return count;
}
