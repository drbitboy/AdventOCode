CPPFLAGS=-g -O0

INPUT_TXT=input.txt

all: constellations

constellations.cpp:: rawdata.h

constellations: constellations.cpp rawdata.h
	$(LINK.cpp) $< $(LOADLIBES) $(LDLIBS) -o $@


rawdata.h: $(INPUT_TXT) Makefile
	sed < $< > $@ -e 's/^/,/' -e '1s/,/RAW_t iraw[][4] = {/' -e '$$s/$$/};/' || ( $(RM) $@ && false )
