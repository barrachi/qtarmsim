#!/usr/bin/make -f

UISRCS:=$(wildcard ui/*.ui)
UIOBJS:=$(UISRCS:%.ui=%.py)

all: ${UIOBJS}

%.py : %.ui
	pyuic4 $< -o $@
