.POSIX:

include config.mk

all: scroll

config.h:
	cp config.def.h config.h

scroll: scroll.c config.h

install: scroll
	mkdir -p $(DESTDIR)$(BINDIR) $(DESTDIR)$(MANDIR)/man1
	cp -f scroll $(DESTDIR)$(BINDIR)
	cp -f scroll.1 $(DESTDIR)$(MANDIR)/man1

uninstall:
	rm -f $(DESTDIR)$(BINDIR)/scroll $(DESTDIR)$(MANDIR)/man1/scroll.1

clean:
	rm -f scroll ptty

distclean: clean
	rm -f config.h scroll-$(VERSION).tar.gz

dist: clean
	mkdir -p scroll-$(VERSION)
	cp -R scroll.1 LICENSE Makefile config.mk config.def.h \
		scroll.c \
		scroll-$(VERSION)
	@if [ -f README ]; then cp README scroll-$(VERSION)/README; elif [ -f ../../../docs/Readmes/st/scroll/README ]; then cp ../../../docs/Readmes/st/scroll/README scroll-$(VERSION)/README; fi
	tar -cf - scroll-$(VERSION) | gzip > scroll-$(VERSION).tar.gz
	rm -rf scroll-$(VERSION)

.c:
	$(CC) $(CFLAGS) $(CPPFLAGS) $(LDFLAGS) -o $@ $< -lutil

.PHONY: all install clean distclean dist
