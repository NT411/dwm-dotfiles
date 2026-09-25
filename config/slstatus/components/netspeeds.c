/* See LICENSE file for copyright and license details. */
#include <limits.h>
#include <stdio.h>
#include <time.h>

#include "../slstatus.h"
#include "../util.h"

static int interface_ready;

void
netspeed_begin_sample(void)
{
	interface_ready = 0;
}

#if defined(__linux__)
	#include <stdint.h>

	#define NET_RX_BYTES "/sys/class/net/%s/statistics/rx_bytes"
	#define NET_TX_BYTES "/sys/class/net/%s/statistics/tx_bytes"

	#include <ifaddrs.h>
	#include <net/if.h>
	#include <string.h>
	#include <sys/socket.h>

	/* Prefer the lowest-metric IPv4 default route. Fall back to an active
	 * addressed interface, including IPv6-only connections. NULL means auto. */
	static const char *
	auto_interface(void)
	{
		static char selected[IF_NAMESIZE];
		char line[512], name[IF_NAMESIZE];
		unsigned long destination, mask, metric, best = ULONG_MAX;
		unsigned int flags;
		struct ifaddrs *addresses, *address;
		FILE *fp;

		if (interface_ready)
			return selected[0] ? selected : NULL;
		interface_ready = 1;
		selected[0] = '\0';
		if ((fp = fopen("/proc/net/route", "r"))) {
			while (fgets(line, sizeof(line), fp)) {
				if (sscanf(line, "%15s %lx %*s %x %*s %*s %lu %lx",
				           name, &destination, &flags, &metric, &mask) != 5)
					continue;
				if (!destination && !mask && (flags & 1) &&
				    !(flags & 0x200) && strcmp(name, "lo") && metric < best) {
					best = metric;
					snprintf(selected, sizeof(selected), "%s", name);
				}
			}
			fclose(fp);
		}
		if (selected[0])
			return selected;
		if (getifaddrs(&addresses) < 0)
			return NULL;
		for (address = addresses; address; address = address->ifa_next) {
			if (!address->ifa_addr || (address->ifa_flags & IFF_LOOPBACK) ||
			    !(address->ifa_flags & IFF_UP) || !(address->ifa_flags & IFF_RUNNING))
				continue;
			if (address->ifa_addr->sa_family != AF_INET &&
			    address->ifa_addr->sa_family != AF_INET6)
				continue;
			if (!selected[0] || strcmp(address->ifa_name, selected) < 0)
				snprintf(selected, sizeof(selected), "%s", address->ifa_name);
		}
		freeifaddrs(addresses);
		return selected[0] ? selected : NULL;
	}

	static const char *
	netspeed(const char *interface, int transmit)
	{
		static uintmax_t previous[2];
		static char previous_interface[2][IF_NAMESIZE];
		static struct timespec previous_time[2];
		struct timespec now;
		uintmax_t bytes, delta;
		double elapsed;
		char path[PATH_MAX];

		if (!interface)
			interface = auto_interface();
		if (!interface ||
		    esnprintf(path, sizeof(path), transmit ? NET_TX_BYTES : NET_RX_BYTES, interface) < 0 ||
		    pscanf(path, "%ju", &bytes) != 1 ||
		    clock_gettime(CLOCK_MONOTONIC, &now) < 0) {
			previous_interface[transmit][0] = '\0';
			return NULL;
		}
		/* Start a fresh sample after switching interfaces or counter resets. */
		delta = strcmp(previous_interface[transmit], interface) || bytes < previous[transmit]
		        ? 0 : bytes - previous[transmit];
		elapsed = (double)(now.tv_sec - previous_time[transmit].tv_sec) +
		          (now.tv_nsec - previous_time[transmit].tv_nsec) / 1E9;
		previous[transmit] = bytes;
		previous_time[transmit] = now;
		snprintf(previous_interface[transmit], IF_NAMESIZE, "%s", interface);
		return fmt_human(elapsed > 0 ? delta / elapsed : 0, 1024);
	}

	const char *
	netspeed_rx(const char *interface)
	{
		return netspeed(interface, 0);
	}

	const char *
	netspeed_tx(const char *interface)
	{
		return netspeed(interface, 1);
	}
#elif defined(__OpenBSD__) | defined(__FreeBSD__)
	#include <ifaddrs.h>
	#include <net/if.h>
	#include <string.h>
	#include <sys/types.h>
	#include <sys/socket.h>

	const char *
	netspeed_rx(const char *interface)
	{
		struct ifaddrs *ifal, *ifa;
		struct if_data *ifd;
		uintmax_t oldrxbytes;
		static uintmax_t rxbytes;
		extern const unsigned int interval;
		int if_ok = 0;

		oldrxbytes = rxbytes;

		if (getifaddrs(&ifal) < 0) {
			warn("getifaddrs failed");
			return NULL;
		}
		rxbytes = 0;
		for (ifa = ifal; ifa; ifa = ifa->ifa_next)
			if (!strcmp(ifa->ifa_name, interface) &&
			   (ifd = (struct if_data *)ifa->ifa_data))
				rxbytes += ifd->ifi_ibytes, if_ok = 1;

		freeifaddrs(ifal);
		if (!if_ok) {
			warn("reading 'if_data' failed");
			return NULL;
		}
		if (oldrxbytes == 0)
			return NULL;

		return fmt_human((rxbytes - oldrxbytes) * 1000 / interval,
		                 1024);
	}

	const char *
	netspeed_tx(const char *interface)
	{
		struct ifaddrs *ifal, *ifa;
		struct if_data *ifd;
		uintmax_t oldtxbytes;
		static uintmax_t txbytes;
		extern const unsigned int interval;
		int if_ok = 0;

		oldtxbytes = txbytes;

		if (getifaddrs(&ifal) < 0) {
			warn("getifaddrs failed");
			return NULL;
		}
		txbytes = 0;
		for (ifa = ifal; ifa; ifa = ifa->ifa_next)
			if (!strcmp(ifa->ifa_name, interface) &&
			   (ifd = (struct if_data *)ifa->ifa_data))
				txbytes += ifd->ifi_obytes, if_ok = 1;

		freeifaddrs(ifal);
		if (!if_ok) {
			warn("reading 'if_data' failed");
			return NULL;
		}
		if (oldtxbytes == 0)
			return NULL;

		return fmt_human((txbytes - oldtxbytes) * 1000 / interval,
		                 1024);
	}
#endif
